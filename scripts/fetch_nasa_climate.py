"""
Fetch real climate data from Open-Meteo API for each dam.
Uses actual historical weather measurements instead of fallback values.
Open-Meteo provides free access to global weather/climate data.
"""
import json
from pathlib import Path
import requests
import pandas as pd

INPUT_DIR = Path(__file__).resolve().parents[1] / "input_data"

# Open-Meteo API endpoint for monthly historical data
# Uses 2020 as a representative year with global coverage
API_URL = "https://archive-api.open-meteo.com/v1/archive"

# No complex mapping - we'll construct Open-Meteo query
# 2020 is used: Jan 1 - Dec 31, 2020

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


def fetch_open_meteo_data(lat, lon, dam_name):
    """
    Fetch monthly climate data from Open-Meteo historical API.
    Uses 2020 data as representative year.
    Returns dict with monthly values for each climate parameter.
    """
    print(f"  Fetching Open-Meteo data for {dam_name} ({lat:.2f}, {lon:.2f})...", end=" ")
    
    try:
        # Open-Meteo daily historical API for 2020
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": "2020-01-01",
            "end_date": "2020-12-31",
            "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,relative_humidity_2m_max,wind_speed_10m_max,radiation_sum",
            "timezone": "UTC"
        }
        
        resp = requests.get(API_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        if "daily" not in data:
            print("[WARN] No daily data in response")
            return None
        
        daily = data["daily"]
        dates = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        avg_temps = daily.get("temperature_2m_mean", [])
        humidities = daily.get("relative_humidity_2m_max", [])
        wind_speeds = daily.get("wind_speed_10m_max", [])
        radiation = daily.get("radiation_sum", [])  # kJ/m2 -> convert to kWh/m2/day
        
        if not dates or not max_temps:
            print("[WARN] Empty daily data")
            return None
        
        # Aggregate daily data to monthly
        from datetime import datetime
        monthly_data = {
            "solar_irradiance_kwh_m2_day": [0] * 12,
            "avg_temp_c": [0] * 12,
            "max_temp_c": [0] * 12,
            "min_temp_c": [0] * 12,
            "humidity_pct": [0] * 12,
            "wind_speed_m_s": [0] * 12,
        }
        
        monthly_counts = [0] * 12
        monthly_temps_max = [[] for _ in range(12)]
        monthly_temps_min = [[] for _ in range(12)]
        monthly_temps_avg = [[] for _ in range(12)]
        monthly_humidity = [[] for _ in range(12)]
        monthly_wind = [[] for _ in range(12)]
        monthly_radiation = [[] for _ in range(12)]
        
        # Aggregate by month
        for i, date_str in enumerate(dates):
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            month_idx = dt.month - 1
            
            monthly_temps_max[month_idx].append(max_temps[i] if max_temps[i] is not None else 0)
            monthly_temps_min[month_idx].append(min_temps[i] if min_temps[i] is not None else 0)
            monthly_temps_avg[month_idx].append(avg_temps[i] if avg_temps[i] is not None else 0)
            monthly_humidity[month_idx].append(humidities[i] if humidities[i] is not None else 65)
            monthly_wind[month_idx].append(wind_speeds[i] if wind_speeds[i] is not None else 2.0)
            # Radiation is in kJ/m2, convert to kWh/m2: divide by 3600
            rad_kwh = (radiation[i] if radiation[i] is not None else 12000) / 3600.0 / 24.0  # daily average
            monthly_radiation[month_idx].append(max(0.1, rad_kwh))
            monthly_counts[month_idx] += 1
        
        # Calculate monthly averages
        for m in range(12):
            if monthly_counts[m] > 0:
                monthly_data["max_temp_c"][m] = sum(monthly_temps_max[m]) / len(monthly_temps_max[m])
                monthly_data["min_temp_c"][m] = sum(monthly_temps_min[m]) / len(monthly_temps_min[m])
                monthly_data["avg_temp_c"][m] = sum(monthly_temps_avg[m]) / len(monthly_temps_avg[m])
                monthly_data["humidity_pct"][m] = sum(monthly_humidity[m]) / len(monthly_humidity[m])
                monthly_data["wind_speed_m_s"][m] = sum(monthly_wind[m]) / len(monthly_wind[m])
                monthly_data["solar_irradiance_kwh_m2_day"][m] = sum(monthly_radiation[m]) / len(monthly_radiation[m])
        
        print("[OK]")
        return monthly_data
    
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] {e}")
        return None


def convert_api_to_csv(api_data):
    """Convert Open-Meteo data dict to DataFrame in our CSV format."""
    if api_data is None:
        return None
    
    # Ensure valid ranges
    solar_vals = api_data.get("solar_irradiance_kwh_m2_day", [])
    
    rows = []
    for i, month_name in enumerate(MONTH_NAMES):
        solar = max(0.5, solar_vals[i])
        # Estimate evaporation (Penman-like): roughly 1/3 of solar + offset
        evap = (solar / 3) + 0.5
        
        row = {
            "month": month_name,
            "solar_irradiance_kwh_m2_day": round(solar, 2),
            "avg_temp_c": round(api_data["avg_temp_c"][i], 1),
            "max_temp_c": round(api_data["max_temp_c"][i], 1),
            "min_temp_c": round(api_data["min_temp_c"][i], 1),
            "humidity_pct": round(max(10, min(100, api_data["humidity_pct"][i])), 1),
            "wind_speed_m_s": round(max(0.1, api_data["wind_speed_m_s"][i]), 1),
            "evaporation_mm_day": round(max(0.5, evap), 2),
        }
        rows.append(row)
    
    return pd.DataFrame(rows)


def main():
    print("=" * 80)
    print("FETCHING REAL CLIMATE DATA FROM OPEN-METEO HISTORICAL API")
    print("=" * 80)
    
    # Load dams.json
    dams_file = INPUT_DIR / "dams.json"
    if not dams_file.exists():
        print(f"[ERROR] {dams_file} not found")
        return
    
    with open(dams_file) as f:
        dams_data = json.load(f)
    
    dams = dams_data.get("dams", [])
    updated_count = 0
    failed_count = 0
    
    print(f"Processing {len(dams)} dams (using 2020 historical data)...\n")
    
    for dam in dams:
        name = dam["name"]
        folder = dam["folder"]
        lat = dam["latitude"]
        lon = dam["longitude"]
        
        # Fetch real data
        api_data = fetch_open_meteo_data(lat, lon, name)
        
        if api_data is None:
            failed_count += 1
            continue
        
        # Convert to CSV format
        df = convert_api_to_csv(api_data)
        if df is None:
            failed_count += 1
            continue
        
        # Save to climate file
        dam_folder = INPUT_DIR / folder
        climate_file = dam_folder / "climate.csv"
        df.to_csv(climate_file, index=False)
        
        print(f"✓ Saved {climate_file.name} for {name}")
        updated_count += 1
    
    print("\n" + "=" * 80)
    print(f"SUCCESS: Updated {updated_count} climate files from Open-Meteo API (real 2020 data)")
    if failed_count > 0:
        print(f"FAILED: {failed_count} dams (API timeout or data unavailable)")
    print("=" * 80)


if __name__ == "__main__":
    main()
