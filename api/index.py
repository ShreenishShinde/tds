from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import json
import math

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

DATA_PATH = Path(__file__).resolve().parent.parent / "data.json"
with DATA_PATH.open("r", encoding="utf-8") as f:
    TELEMETRY = json.load(f)


def percentile95(values):
    """Linear-interpolated 95th percentile (same convention as numpy default)."""
    values = sorted(values)
    if len(values) == 1:
        return values[0]
    pos = 0.95 * (len(values) - 1)
    lower = math.floor(pos)
    upper = math.ceil(pos)
    if lower == upper:
        return values[lower]
    return values[lower] + (values[upper] - values[lower]) * (pos - lower)


@app.post("/")
@app.post("/api/latency")
@app.post("/latency")
async def latency_metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = float(body.get("threshold_ms", 180))

    if not isinstance(regions, list):
        return JSONResponse(status_code=400, content={"error": "'regions' must be a list"})

    result = {}
    for region in regions:
        records = [r for r in TELEMETRY if r.get("region") == region]
        if not records:
            result[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0,
            }
            continue
        latencies = [float(r["latency_ms"]) for r in records]
        uptimes = [float(r["uptime_pct"]) for r in records]
        result[region] = {
            "avg_latency": sum(latencies) / len(latencies),
            "p95_latency": percentile95(latencies),
            "avg_uptime": sum(uptimes) / len(uptimes),
            "breaches": sum(value > threshold for value in latencies),
        }
    return result
