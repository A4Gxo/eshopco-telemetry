
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
import os

app = FastAPI()

# Enable CORS for all POST requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry once at startup
telemetry_file = os.path.join(os.path.dirname(__file__), "..", "telemetry.json")
with open(telemetry_file, "r") as f:
    TELEMETRY = json.load(f)

@app.post("/")
async def check_latency(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    response = {}
    for region in regions:
        records = [rec for rec in TELEMETRY if rec["region"] == region]

        if not records:
            response[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": None,
            }
            continue

        latencies = np.array([rec["latency_ms"] for rec in records])
        uptimes = np.array([rec["uptime"] for rec in records])

        avg_latency = float(np.mean(latencies))
        p95_latency = float(np.percentile(latencies, 95))
        avg_uptime = float(np.mean(uptimes))
        breaches = int(np.sum(latencies > threshold))

        response[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 4),
            "breaches": breaches,
        }

    return response
