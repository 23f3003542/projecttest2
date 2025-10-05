from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import os

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

# Sample data - replace with actual data file loading
DATA = [
    {"region": "emea", "latency_ms": 150, "uptime_pct": 99.5},
    {"region": "emea", "latency_ms": 180, "uptime_pct": 99.2},
    {"region": "emea", "latency_ms": 140, "uptime_pct": 99.7},
    {"region": "amer", "latency_ms": 90, "uptime_pct": 99.9},
    {"region": "amer", "latency_ms": 110, "uptime_pct": 99.7},
    {"region": "amer", "latency_ms": 160, "uptime_pct": 99.5},
    {"region": "apac", "latency_ms": 120, "uptime_pct": 99.8},
    {"region": "apac", "latency_ms": 200, "uptime_pct": 99.1},
]

# Try to load data from file if available
try:
    import os
    data_file = os.path.join(os.path.dirname(__file__), "q-vercel-latency.json")
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            DATA = json.load(f)
except:
    pass  # Use default data


def calculate_percentile(values, percentile):
    """Calculate percentile without numpy"""
    if not values:
        return 0
    sorted_values = sorted(values)
    n = len(sorted_values)
    index = (percentile / 100) * (n - 1)
    
    if index.is_integer():
        return sorted_values[int(index)]
    else:
        lower = sorted_values[int(index)]
        upper = sorted_values[int(index) + 1]
        return lower + (upper - lower) * (index - int(index))


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
            # Filter data for this region
            region_data = [record for record in DATA if record["region"] == region]

            if region_data:
                latencies = [record["latency_ms"] for record in region_data]
                uptimes = [record["uptime_pct"] for record in region_data]
                
                avg_latency = round(sum(latencies) / len(latencies), 2)
                p95_latency = round(calculate_percentile(latencies, 95), 2)
                avg_uptime = round(sum(uptimes) / len(uptimes), 3)
                breaches = len([l for l in latencies if l > threshold])

                results.append({
                    "region": region,
                    "avg_latency": avg_latency,
                    "p95_latency": p95_latency,
                    "avg_uptime": avg_uptime,
                    "breaches": breaches,
                })

        return {"regions": results}
    except Exception as e:
        return {"error": str(e), "regions": []}

# Export the app for Vercel
handler = app
