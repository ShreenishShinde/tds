
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pathlib import Path
import json
import math

app = FastAPI()

@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    if request.method == "OPTIONS":
        response = JSONResponse(content={})
    else:
        response = await call_next(request)

    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

with (Path(__file__).resolve().parent / "data.json").open() as f:
    DATA = json.load(f)

def percentile95(values):
    values = sorted(values)
    if len(values) == 1:
        return values[0]
    pos = 0.95 * (len(values) - 1)
    lo, hi = math.floor(pos), math.ceil(pos)
    return values[lo] + (values[hi] - values[lo]) * (pos - lo)

async def calculate_metrics(request: Request):
    body = await request.json()
    threshold = float(body.get("threshold_ms", 180))
    result = {}

    for region in body.get("regions", []):
        rows = [r for r in DATA if r["region"] == region]
        if not rows:
            result[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0
            }
            continue

        latency = [float(r["latency_ms"]) for r in rows]
        uptime = [float(r["uptime_pct"]) for r in rows]

        result[region] = {
            "avg_latency": sum(latency) / len(latency),
            "p95_latency": percentile95(latency),
            "avg_uptime": sum(uptime) / len(uptime),
            "breaches": sum(x > threshold for x in latency)
        }

    return result

app.post("/")(calculate_metrics)
app.post("/latency")(calculate_metrics)
app.post("/api/latency")(calculate_metrics)
