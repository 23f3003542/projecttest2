#!/usr/bin/env python3
"""
Test script for the Vercel latency API
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path

# Test the logic directly without the web server
def test_logic():
    print("Testing API logic directly...")
    
    # Load the data
    data_file = Path("api/q-vercel-latency.json")
    df = pd.read_json(data_file)
    
    print(f"Loaded {len(df)} records")
    print("Available regions:", df['region'].unique().tolist())
    
    # Test calculations
    regions_to_process = ["emea", "apac"]
    threshold = 180
    
    results = []
    
    for region in regions_to_process:
        region_df = df[df["region"] == region]
        
        if not region_df.empty:
            avg_latency = round(region_df["latency_ms"].mean(), 2)
            p95_latency = round(np.percentile(region_df["latency_ms"], 95), 2)
            avg_uptime = round(region_df["uptime_pct"].mean(), 3)
            breaches = int(region_df[region_df["latency_ms"] > threshold].shape[0])
            
            result = {
                "region": region,
                "avg_latency": avg_latency,
                "p95_latency": p95_latency,
                "avg_uptime": avg_uptime,
                "breaches": breaches,
            }
            results.append(result)
            print(f"Region {region}: {result}")
    
    response = {"regions": results}
    print("\nFinal response:", json.dumps(response, indent=2))
    return response

if __name__ == "__main__":
    test_logic()