
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pathlib import Path
import json
import math

app = FastAPI()


# Enable CORS for all origins, including OPTIONS preflight requests.
@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        response = JSONResponse(content={})
    else:
        response = await call_next(request)

    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


# Load the telemetry file from the repository root.
DATA_PATH = Path(__file__).resolve().parent / "q-vercel-latency.json"

with DATA_PATH.open("r", encoding="utf-8") as f:
    TELEMETRY = json.load(f)


def percentile95(values):
    """Calculate the linearly interpolated 95th percentile."""
    values = sorted(values)

    if len(values) == 1:
        return values[0]

    position = 0.95 * (len(values) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return values[lower]

    return (
        values[lower]
        + (values[upper] - values[lower]) * (position - lower)
    )


async def latency_metrics(request: Request):
    body = await request.json()

    regions = body.get("regions", [])
    threshold = float(body.get("threshold_ms", 180))

    if not isinstance(regions, list):
        return JSONResponse(
            status_code=400,
            content={"error": "'regions' must be a list"}
        )

    result = {}

    for region in regions:
        records = [
            record for record in TELEMETRY
            if record.get("region") == region
        ]

        if not records:
            result[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0
            }
            continue

        latencies = [
            float(record["latency_ms"]) for record in records
        ]

        uptimes = [
            float(record["uptime_pct"]) for record in records
        ]

        result[region] = {
            "avg_latency": sum(latencies) / len(latencies),
            "p95_latency": percentile95(latencies),
            "avg_uptime": sum(uptimes) / len(uptimes),
            "breaches": sum(
                latency > threshold for latency in latencies
            )
        }

    return result


# Support the root URL and the likely assignment endpoint paths.
app.post("/")(latency_metrics)
app.post("/api/latency")(latency_metrics)
app.post("/latency")(latency_metrics)
