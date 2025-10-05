from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from pathlib import Path
import json

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Load the dataset once when the app starts
# The data file should be in the same directory as this script
DATA_FILE = Path(__file__).parent / "q-vercel-latency.json"

try:
    df = pd.read_json(DATA_FILE)
except Exception as e:
    # Fallback data if file not found
    df = pd.DataFrame([
        {"region": "emea", "latency_ms": 150, "uptime_pct": 99.5},
        {"region": "emea", "latency_ms": 180, "uptime_pct": 99.2},
        {"region": "emea", "latency_ms": 140, "uptime_pct": 99.7},
        {"region": "amer", "latency_ms": 90, "uptime_pct": 99.9},
        {"region": "amer", "latency_ms": 110, "uptime_pct": 99.7},
        {"region": "amer", "latency_ms": 160, "uptime_pct": 99.5},
    ])


@app.get("/")
async def root():
    return {"message": "Vercel Latency Analytics API is running."}


@app.post("/api/")
async def get_latency_stats(request: Request):
    try:
        payload = await request.json()
        regions_to_process = payload.get("regions", [])
        threshold = payload.get("threshold_ms", 200)

        results = []

        for region in regions_to_process:
            region_df = df[df["region"] == region]

            if not region_df.empty:
                avg_latency = float(round(region_df["latency_ms"].mean(), 2))
                p95_latency = float(round(np.percentile(region_df["latency_ms"], 95), 2))
                avg_uptime = float(round(region_df["uptime_pct"].mean(), 3))
                breaches = int(region_df[region_df["latency_ms"] > threshold].shape[0])

                results.append(
                    {
                        "region": region,
                        "avg_latency": avg_latency,
                        "p95_latency": p95_latency,
                        "avg_uptime": avg_uptime,
                        "breaches": breaches,
                    }
                )

        return {"regions": results}
    except Exception as e:
        return {"error": str(e), "regions": []}
