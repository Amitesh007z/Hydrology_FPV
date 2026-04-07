#!/usr/bin/env python3
"""
Generate dams.json index from already-created folders
"""

import os
import json
from pathlib import Path
import pandas as pd

input_data = Path("input_data")
dams = []

print("Scanning input_data/ for dam folders...")

for folder in sorted(input_data.iterdir()):
    if folder.is_dir() and (folder / "reservoir.csv").exists():
        try:
            # Read reservoir CSV
            df_res = pd.read_csv(folder / "reservoir.csv")
            row = df_res.iloc[0]
            
            # Read climate CSV if available
            climate_count = 0
            if (folder / "climate.csv").exists():
                df_clim = pd.read_csv(folder / "climate.csv")
                climate_count = len(df_clim)
            
            dam_entry = {
                "name": str(row.get("reservoir_name", folder.name)),
                "folder": folder.name,
                "state": str(row.get("state", "")),
                "river": str(row.get("river", "")),
                "latitude": float(row.get("latitude", 0)),
                "longitude": float(row.get("longitude", 0)),
                "area_km2": float(row.get("area_km2", 0)),
                "head_m": float(row.get("head_m", 0)),
                "capacity_mw": float(row.get("installed_capacity_mw", 0)),
                "storage_mcm": float(row.get("gross_storage_mcm", 0)),
                "climate_months": climate_count,
                "status": "Complete" if climate_count == 12 else "Partial"
            }
            
            dams.append(dam_entry)
            print(f"  [OK] {dam_entry['name']} ({dam_entry['latitude']}N, {dam_entry['longitude']}E)")
            
        except Exception as e:
            print(f"  [ERR] {folder.name}: {str(e)[:50]}")

# Create dams.json
dams_json = {
    "total": len(dams),
    "complete": sum(1 for d in dams if d["status"] == "Complete"),
    "timestamp": "2026-04-07",
    "dams": dams
}

with open("input_data/dams.json", "w") as f:
    json.dump(dams_json, f, indent=2)

print(f"\n[SUCCESS] Created dams.json with {len(dams)} dams")
print(f"  Complete: {dams_json['complete']}")
print(f"  Location: input_data/dams.json")
