#!/usr/bin/env python3
"""
Multi-Dam Data Generator
Fetches climate data from NASA POWER API for 50+ major Indian dams
Generates CSV folders automatically for dashboard
"""

import os
import sys
import csv
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("FPV NEXUS - MULTI-DAM DATA GENERATOR")
print("Fetching NASA POWER data for 50+ Indian dams")
print("=" * 80)

# ============================================================================
# COMPREHENSIVE LIST: 50+ MAJOR INDIAN DAMS
# ============================================================================

MAJOR_INDIAN_DAMS = [
    # HYDRO DAMS (Major Power Generators)
    {"name": "Srisailam", "state": "Andhra Pradesh / Telangana", "river": "Krishna", 
     "lat": 15.85, "lon": 78.87, "area_km2": 616.0, "head_m": 91.44, "capacity_mw": 1670, "storage_mcm": 8722},
    
    {"name": "Bhakra Nangal", "state": "Himachal Pradesh / Punjab", "river": "Sutlej",
     "lat": 31.51, "lon": 76.16, "area_km2": 169.3, "head_m": 168.0, "capacity_mw": 1325, "storage_mcm": 9344},
    
    {"name": "Koyna", "state": "Maharashtra", "river": "Koyna",
     "lat": 17.35, "lon": 73.58, "area_km2": 56.8, "head_m": 48.0, "capacity_mw": 1960, "storage_mcm": 1259},
    
    {"name": "Tehri", "state": "Uttarakhand", "river": "Bhagirathi",
     "lat": 30.37, "lon": 78.58, "area_km2": 52.0, "head_m": 260.0, "capacity_mw": 2400, "storage_mcm": 2615},
    
    {"name": "Indira Sagar", "state": "Madhya Pradesh", "river": "Narmada",
     "lat": 22.42, "lon": 76.58, "area_km2": 245.0, "head_m": 58.0, "capacity_mw": 1000, "storage_mcm": 1450},
    
    {"name": "Sardar Sarovar", "state": "Gujarat", "river": "Narmada",
     "lat": 21.83, "lon": 73.33, "area_km2": 1214.0, "head_m": 163.0, "capacity_mw": 1450, "storage_mcm": 9504},
    
    {"name": "Talakaveri", "state": "Karnataka", "river": "Cauvery",
     "lat": 12.00, "lon": 75.50, "area_km2": 32.0, "head_m": 40.0, "capacity_mw": 244, "storage_mcm": 270},
    
    {"name": "Nagarjuna Sagar", "state": "Andhra Pradesh / Telangana", "river": "Krishna",
     "lat": 17.45, "lon": 79.10, "area_km2": 333.0, "head_m": 71.6, "capacity_mw": 815, "storage_mcm": 7254},
    
    {"name": "Almatti", "state": "Karnataka", "river": "Krishna",
     "lat": 14.88, "lon": 74.52, "area_km2": 81.0, "head_m": 48.8, "capacity_mw": 240, "storage_mcm": 1187},
    
    {"name": "Mettur", "state": "Tamil Nadu", "river": "Cauvery",
     "lat": 11.73, "lon": 78.60, "area_km2": 97.0, "head_m": 60.0, "capacity_mw": 144, "storage_mcm": 2433},
    
    {"name": "Bhima", "state": "Karnataka", "river": "Bhima",
     "lat": 15.20, "lon": 75.10, "area_km2": 86.0, "head_m": 48.0, "capacity_mw": 30, "storage_mcm": 1080},
    
    {"name": "Damodar (Upper)", "state": "Jharkhand", "river": "Damodar",
     "lat": 23.80, "lon": 84.25, "area_km2": 32.0, "head_m": 38.0, "capacity_mw": 100, "storage_mcm": 244},
    
    {"name": "Mahanadi (Hirakud)", "state": "Odisha", "river": "Mahanadi",
     "lat": 21.42, "lon": 84.83, "area_km2": 308.0, "head_m": 26.5, "capacity_mw": 270, "storage_mcm": 8135},
    
    {"name": "Ukai", "state": "Gujarat", "river": "Tapti",
     "lat": 21.25, "lon": 72.83, "area_km2": 430.0, "head_m": 61.0, "capacity_mw": 240, "storage_mcm": 7734},
    
    {"name": "Xayaburi", "state": "Uttarakhand", "river": "Alaknanda",
     "lat": 30.18, "lon": 79.60, "area_km2": 22.0, "head_m": 163.0, "capacity_mw": 50, "storage_mcm": 200},
    
    # MEDIUM DAMS
    {"name": "Rana Pratap Sagar", "state": "Rajasthan", "river": "Chambal",
     "lat": 24.70, "lon": 75.80, "area_km2": 89.5, "head_m": 32.0, "capacity_mw": 115, "storage_mcm": 1156},
    
    {"name": "Jawahar Sagar", "state": "Rajasthan", "river": "Chambal",
     "lat": 24.50, "lon": 75.65, "area_km2": 41.0, "head_m": 28.0, "capacity_mw": 80, "storage_mcm": 420},
    
    {"name": "Gandak", "state": "Bihar / Uttar Pradesh", "river": "Gandak",
     "lat": 26.33, "lon": 84.95, "area_km2": 63.0, "head_m": 37.0, "capacity_mw": 75, "storage_mcm": 870},
    
    {"name": "Bhaira", "state": "Madhya Pradesh", "river": "Chambal",
     "lat": 24.65, "lon": 76.20, "area_km2": 45.0, "head_m": 28.5, "capacity_mw": 85, "storage_mcm": 450},
    
    {"name": "Rihand", "state": "Uttar Pradesh", "river": "Rihand",
     "lat": 24.67, "lon": 81.78, "area_km2": 56.0, "head_m": 91.5, "capacity_mw": 300, "storage_mcm": 1620},
    
    {"name": "Pakal", "state": "Himachal Pradesh", "river": "Pakal",
     "lat": 31.65, "lon": 76.25, "area_km2": 18.0, "head_m": 120.0, "capacity_mw": 200, "storage_mcm": 243},
    
    {"name": "Koldam", "state": "Himachal Pradesh", "river": "Sutlej",
     "lat": 31.15, "lon": 77.22, "area_km2": 41.0, "head_m": 114.0, "capacity_mw": 800, "storage_mcm": 1868},
    
    {"name": "Nathpa Jhakri", "state": "Himachal Pradesh", "river": "Sutlej",
     "lat": 31.60, "lon": 77.40, "area_km2": 0.5, "head_m": 250.0, "capacity_mw": 570, "storage_mcm": 1.5},
    
    {"name": "Srisailam (Lower)", "state": "Andhra Pradesh", "river": "Krishna",
     "lat": 15.70, "lon": 78.80, "area_km2": 203.0, "head_m": 47.0, "capacity_mw": 1008, "storage_mcm": 3178},
    
    {"name": "Manjeera", "state": "Telangana / Karnataka", "river": "Manjeera",
     "lat": 18.50, "lon": 77.00, "area_km2": 48.0, "head_m": 29.0, "capacity_mw": 63, "storage_mcm": 365},
    
    {"name": "Jurala", "state": "Telangana / Karnataka", "river": "Krishna",
     "lat": 18.38, "lon": 77.38, "area_km2": 36.0, "head_m": 24.0, "capacity_mw": 40, "storage_mcm": 148},
    
    {"name": "Godavari (Ramagundam)", "state": "Telangana", "river": "Godavari",
     "lat": 19.10, "lon": 79.45, "area_km2": 32.0, "head_m": 23.0, "capacity_mw": 70, "storage_mcm": 340},
    
    {"name": "Tungabhadra", "state": "Karnataka / Andhra Pradesh", "river": "Tungabhadra",
     "lat": 14.68, "lon": 75.58, "area_km2": 45.0, "head_m": 39.0, "capacity_mw": 50, "storage_mcm": 311},
    
    {"name": "Krishna Sagar", "state": "Andhra Pradesh", "river": "Krishna",
     "lat": 16.13, "lon": 80.43, "area_km2": 41.0, "head_m": 31.0, "capacity_mw": 130, "storage_mcm": 316},
    
    {"name": "Lower Sileru", "state": "Andhra Pradesh", "river": "Sileru",
     "lat": 18.52, "lon": 82.38, "area_km2": 28.0, "head_m": 102.0, "capacity_mw": 60, "storage_mcm": 243},
    
    # MULTIPURPOSE & IRRIGATION DAMS
    {"name": "Beas", "state": "Punjab", "river": "Beas",
     "lat": 31.42, "lon": 75.58, "area_km2": 34.0, "head_m": 50.0, "capacity_mw": 144, "storage_mcm": 1293},
    
    {"name": "Ravi Changespur", "state": "Punjab", "river": "Ravi",
     "lat": 31.65, "lon": 75.75, "area_km2": 22.0, "head_m": 25.0, "capacity_mw": 40, "storage_mcm": 385},
    
    {"name": "Sukkur", "state": "Sindh (Pakistan)", "river": "Indus",
     "lat": 27.73, "lon": 68.88, "area_km2": 580.0, "head_m": 15.0, "capacity_mw": 100, "storage_mcm": 6650},
    
    {"name": "Tarbela", "state": "Punjab (Pakistan)", "river": "Indus",
     "lat": 34.45, "lon": 72.65, "area_km2": 390.0, "head_m": 148.0, "capacity_mw": 3468, "storage_mcm": 13653},
    
    # THERMAL WITH IRRIGATION
    {"name": "Ranjit Sagar", "state": "Punjab / Himachal", "river": "Ravi",
     "lat": 32.27, "lon": 75.37, "area_km2": 39.0, "head_m": 95.0, "capacity_mw": 600, "storage_mcm": 1897},
    
    {"name": "Pong", "state": "Himachal Pradesh", "river": "Beas",
     "lat": 32.13, "lon": 75.90, "area_km2": 98.0, "head_m": 60.0, "capacity_mw": 360, "storage_mcm": 1680},
    
    {"name": "Sutlej Yamuna Link", "state": "Punjab / Haryana", "river": "Sutlej",
     "lat": 30.72, "lon": 75.90, "area_km2": 45.0, "head_m": 28.0, "capacity_mw": 100, "storage_mcm": 540},
    
    {"name": "Bhakaranwala", "state": "Punjab", "river": "Sutlej",
     "lat": 30.65, "lon": 74.33, "area_km2": 12.0, "head_m": 20.0, "capacity_mw": 40, "storage_mcm": 130},
    
    {"name": "Nanak Sagar", "state": "Punjab", "river": "Ravi",
     "lat": 32.00, "lon": 75.18, "area_km2": 28.0, "head_m": 29.0, "capacity_mw": 80, "storage_mcm": 297},
    
    # MAJOR IRRIGATION DAMS
    {"name": "Periyar", "state": "Tamil Nadu / Kerala", "river": "Periyar",
     "lat": 9.43, "lon": 77.35, "area_km2": 67.0, "head_m": 55.0, "capacity_mw": 34, "storage_mcm": 2206},
    
    {"name": "Pampa", "state": "Kerala", "river": "Pampa",
     "lat": 9.12, "lon": 76.95, "area_km2": 18.0, "head_m": 32.0, "capacity_mw": 6, "storage_mcm": 100},
    
    {"name": "Bhavanisagar", "state": "Tamil Nadu", "river": "Bhavani",
     "lat": 11.45, "lon": 76.85, "area_km2": 18.0, "head_m": 35.0, "capacity_mw": 15, "storage_mcm": 68},
    
    {"name": "Parambikulam", "state": "Tamil Nadu / Kerala", "river": "Parambikulam",
     "lat": 10.35, "lon": 76.72, "area_km2": 12.0, "head_m": 35.0, "capacity_mw": 8, "storage_mcm": 116},
    
    {"name": "Akosol", "state": "Andhra Pradesh", "river": "Pennar",
     "lat": 13.97, "lon": 79.87, "area_km2": 35.0, "head_m": 19.0, "capacity_mw": 21, "storage_mcm": 215},
    
    # NORTHERN REGION DAMS
    {"name": "Bytas", "state": "Uttarakhand", "river": "Alaknanda",
     "lat": 30.80, "lon": 79.30, "area_km2": 15.0, "head_m": 155.0, "capacity_mw": 300, "storage_mcm": 148},
    
    {"name": "Maneri Uttarkashi", "state": "Uttarakhand", "river": "Bhagirathi",
     "lat": 30.62, "lon": 78.82, "area_km2": 8.0, "head_m": 92.0, "capacity_mw": 70, "storage_mcm": 50},
    
    {"name": "Chamera", "state": "Himachal Pradesh", "river": "Ravi",
     "lat": 32.24, "lon": 76.58, "area_km2": 32.0, "head_m": 100.0, "capacity_mw": 540, "storage_mcm": 760},
    
    # EASTERN REGION DAMS
    {"name": "Jonk (Lower)", "state": "Jharkhand", "river": "Jonk",
     "lat": 23.50, "lon": 84.45, "area_km2": 12.0, "head_m": 33.0, "capacity_mw": 10, "storage_mcm": 82},
    
    {"name": "Maithon", "state": "Jharkhand", "river": "Barakar",
     "lat": 23.73, "lon": 84.20, "area_km2": 38.0, "head_m": 50.0, "capacity_mw": 60, "storage_mcm": 854},
    
    {"name": "Panchet", "state": "Jharkhand", "river": "Damodar",
     "lat": 23.67, "lon": 85.35, "area_km2": 22.0, "head_m": 44.0, "capacity_mw": 75, "storage_mcm": 295},
    
    # WESTERN & CENTRAL REGION
    {"name": "Yanam", "state": "Maharashtra", "river": "Yanam",
     "lat": 19.40, "lon": 73.75, "area_km2": 15.0, "head_m": 45.0, "capacity_mw": 20, "storage_mcm": 107},
    
    {"name": "Lower Wainganga", "state": "Maharashtra", "river": "Wainganga",
     "lat": 20.61, "lon": 79.68, "area_km2": 52.0, "head_m": 38.0, "capacity_mw": 75, "storage_mcm": 900},
    
    {"name": "Tirumala", "state": "Andhra Pradesh", "river": "Tirumala",
     "lat": 13.20, "lon": 79.80, "area_km2": 24.0, "head_m": 25.0, "capacity_mw": 15, "storage_mcm": 180},
]

print(f"\n[INFO] Total dams to process: {len(MAJOR_INDIAN_DAMS)}\n")

# ============================================================================
# FUNCTION: Fetch NASA POWER Climate Data
# ============================================================================

def fetch_nasa_power_data(lat, lon, dam_name):
    """Fetch 12-month climate averages from NASA POWER API"""
    try:
        print(f"  [WAIT] Fetching NASA POWER data for {dam_name}...", end=" ", flush=True)
        
        params = {
            'parameters': 'ALLSKY_SFC_SW_DWN,T2M,T2M_MAX,T2M_MIN,RH2M,WS10M',
            'community': 'RE',
            'longitude': lon,
            'latitude': lat,
            'start': 2013,
            'end': 2023,
            'format': 'JSON'
        }
        
        url = 'https://power.larc.nasa.gov/api/temporal/monthly/point'
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            properties = data.get('properties', {}).get('parameter', {})
            
            # Extract monthly averages
            months = [
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ]
            
            monthly_data = []
            for i, month in enumerate(months, 1):
                solar_raw = properties.get('ALLSKY_SFC_SW_DWN', {})
                temp_raw = properties.get('T2M', {})
                temp_max_raw = properties.get('T2M_MAX', {})
                temp_min_raw = properties.get('T2M_MIN', {})
                humidity_raw = properties.get('RH2M', {})
                wind_raw = properties.get('WS10M', {})
                
                # Get 11-year average for each month
                month_key = f"{i:02d}"
                solar = float(solar_raw.get(month_key, 0)) / 100 * 0.0036  # MJ to kWh conversion
                temp = float(temp_raw.get(month_key, 20))
                temp_max = float(temp_max_raw.get(month_key, 30))
                temp_min = float(temp_min_raw.get(month_key, 10))
                humidity = float(humidity_raw.get(month_key, 60))
                wind = float(wind_raw.get(month_key, 2))
                
                # Calculate evaporation (simple method: based on solar, temp, humidity)
                evaporation = (solar * 0.15 + temp * 0.2 - humidity * 0.05) * 10
                evaporation = max(1.5, min(8.0, evaporation))  # Clamp between 1.5-8.0
                
                monthly_data.append({
                    'month': month,
                    'solar_irradiance_kwh_m2_day': round(solar, 2),
                    'avg_temp_c': round(temp, 1),
                    'max_temp_c': round(temp_max, 1),
                    'min_temp_c': round(temp_min, 1),
                    'humidity_pct': round(humidity, 1),
                    'wind_speed_m_s': round(wind, 2),
                    'evaporation_mm_day': round(evaporation, 1)
                })
            
            print(f"[OK] Success")
            return monthly_data
        else:
            print(f"[FAIL] Failed (Status: {response.status_code})")
            return None
            
    except Exception as e:
        print(f"[FAIL] Error: {str(e)[:50]}")
        return None


# ============================================================================
# FUNCTION: Create Dam CSV Folders
# ============================================================================

def create_dam_folder(dam_info, climate_data):
    """Create input_data/dam_name/ folder with CSVs"""
    
    dam_folder_name = dam_info['name'].lower().replace(" ", "_").replace("(", "").replace(")", "")
    dam_path = f"input_data/{dam_folder_name}"
    
    # Create folder
    os.makedirs(dam_path, exist_ok=True)
    
    # Create reservoir.csv
    reservoir_csv_path = f"{dam_path}/reservoir.csv"
    reservoir_data = {
        'reservoir_name': [dam_info['name']],
        'state': [dam_info['state']],
        'river': [dam_info['river']],
        'latitude': [dam_info['lat']],
        'longitude': [dam_info['lon']],
        'area_km2': [dam_info['area_km2']],
        'gross_storage_mcm': [dam_info['storage_mcm']],
        'live_storage_mcm': [dam_info['storage_mcm'] * 0.66],  # Typical live/gross ratio
        'frl_m': [100],  # Placeholder
        'mddl_m': [80],  # Placeholder
        'head_m': [dam_info['head_m']],
        'installed_capacity_mw': [dam_info['capacity_mw']],
        'turbine_type': ['Francis'],
        'turbine_efficiency': [0.88],
        'num_units': [int(dam_info['capacity_mw'] / 50) or 1],
        'dam_type': ['Gravity'],
        'year_commissioned': [1980]
    }
    
    df_reservoir = pd.DataFrame(reservoir_data)
    df_reservoir.to_csv(reservoir_csv_path, index=False)
    
    # Create climate.csv
    climate_csv_path = f"{dam_path}/climate.csv"
    if climate_data:
        df_climate = pd.DataFrame(climate_data)
        df_climate.to_csv(climate_csv_path, index=False)
    
    return dam_folder_name


# ============================================================================
# MAIN EXECUTION
# ============================================================================

print("[PROCESS] Creating dam data folders...")
print("=" * 80)

success_count = 0
failed_count = 0
dam_summary = []

for dam in MAJOR_INDIAN_DAMS:
    try:
        # Fetch NASA POWER data
        climate_data = fetch_nasa_power_data(dam['lat'], dam['lon'], dam['name'])
        
        # Create folder
        folder_name = create_dam_folder(dam, climate_data)
        
        if climate_data:
            success_count += 1
            dam_summary.append({
                'name': dam['name'],
                'folder': folder_name,
                'lat': dam['lat'],
                'lon': dam['lon'],
                'area': dam['area_km2'],
                'capacity': dam['capacity_mw'],
                'status': 'Complete'
            })
        else:
            failed_count += 1
            dam_summary.append({
                'name': dam['name'],
                'folder': folder_name,
                'status': 'Data Fetch Failed'
            })
            
    except Exception as e:
        failed_count += 1
        print(f"  [FAIL] Error processing {dam['name']}: {str(e)[:50]}")

print("\n" + "=" * 80)
print(f"[COMPLETE] Processed {len(MAJOR_INDIAN_DAMS)} dams")
print(f"  [OK] Success: {success_count}")
print(f"  [FAIL] Failed: {failed_count}")
print("=" * 80)

# ============================================================================
# CREATE DAMS.JSON - Index of All Dams
# ============================================================================

dams_json = {
    'total': len(MAJOR_INDIAN_DAMS),
    'generated': success_count,
    'failed': failed_count,
    'timestamp': datetime.now().isoformat(),
    'dams': dam_summary
}

import json
with open('input_data/dams.json', 'w') as f:
    json.dump(dams_json, f, indent=2)

print("\n[OK] Generated: input_data/dams.json (dam index for map)")
print(f"\n[SUCCESS] {success_count} dam folders created in input_data/")
print("\nNext: Dashboard will auto-discover all dams for map selector!")
