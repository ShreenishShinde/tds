from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
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

with (Path(__file__).resolve().parent / "data.json").open(encoding="utf-8") as f:
    DATA = json.load(f)

def percentile95(values):
    values = sorted(values)
    if len(values) == 1:
        return values[0]
    pos = 0.95 * (len(values) - 1)
    lo, hi = math.floor(pos), math.ceil(pos)
    return values[lo] if lo == hi else values[lo] + (values[hi] - values[lo]) * (pos - lo)

@app.post("/")
async def metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = float(body.get("threshold_ms", 180))
    if not isinstance(regions, list):
        return {"error": "'regions' must be a list"}
    result = {}
    for region in regions:
        rows = [r for r in DATA if r.get("region") == region]
        if not rows:
            result[region] = {"avg_latency": None, "p95_latency": None, "avg_uptime": None, "breaches": 0}
            continue
        latency = [float(r["latency_ms"]) for r in rows]
        uptime = [float(r["uptime_pct"]) for r in rows]
        result[region] = {
            "avg_latency": sum(latency) / len(latency),
            "p95_latency": percentile95(latency),
            "avg_uptime": sum(uptime) / len(uptime),
            "breaches": sum(x > threshold for x in latency),
        }
    return result
