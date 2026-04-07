"""
Generate realistic climate data for Indian dams
Based on typical solar patterns for different regions
"""

import pandas as pd
from pathlib import Path

# Realistic solar irradiance by region (kWh/m²/day)
# Based on India's typical solar patterns
REGIONAL_SOLAR = {
    "talakaveri": 4.5,      # Karnataka - moderate
    "koyna": 4.8,            # Maharashtra - good
    "srisailam": 5.2,        # Telangana - very good
    "bhakra_nangal": 4.2,    # HP/Punjab - lower (north)
    "tehri": 4.0,            # Uttarakhand - lower (north, hills)
    "indira_sagar": 5.1,     # MP - very good
    "sardar_sarovar": 5.3,   # Gujarat - excellent
    "nagarjuna_sagar": 5.0,  # Telangana/AP - very good
}

# Monthly variation factors (seasonal)
SOLAR_SEASONALITY = [0.7, 0.75, 0.85, 0.95, 1.0, 0.95, 0.85, 0.8, 0.9, 0.95, 0.7, 0.65]

# Temperature by region (°C)
REGIONAL_TEMP = {
    "talakaveri": 22,        # Karnataka
    "koyna": 21,             # Maharashtra
    "srisailam": 25,         # Telangana
    "bhakra_nangal": 15,     # HP/Punjab (cold)
    "tehri": 14,             # Uttarakhand (cold)
    "indira_sagar": 24,      # MP (hot)
    "sardar_sarovar": 26,    # Gujarat (hot)
    "nagarjuna_sagar": 25,   # Telangana
}

# Wind speed (m/s)
WIND_BY_REGION = {
    "talakaveri": 1.5,
    "koyna": 2.0,
    "srisailam": 2.5,
    "bhakra_nangal": 3.0,
    "tehri": 2.5,
    "indira_sagar": 2.2,
    "sardar_sarovar": 2.8,
    "nagarjuna_sagar": 2.4,
}

MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]

def create_climate_data(dam_name, base_solar, base_temp, base_wind):
    """Create realistic monthly climate data"""
    import math
    months = []
    
    for i, month_name in enumerate(MONTH_NAMES):
        # Solar with seasonality
        solar = base_solar * SOLAR_SEASONALITY[i]
        
        # Temperature variation: coldest in Jan, hottest in June-July
        # Using sine wave: ranges from -8 to +8
        temp_variation = 8 * math.sin((i - 2) * 3.14159 / 6)
        avg_temp = base_temp + temp_variation
        
        # Wind speed seasonal variation
        wind = base_wind * (0.8 + 0.4 * SOLAR_SEASONALITY[i])
        
        # Humidity (varies inversely with temperature)
        humidity = 65 - (avg_temp - base_temp) * 0.5
        
        # Evaporation (Penman-like estimation)
        evap = (solar / 3) + 0.5
        
        months.append({
            "month": month_name,
            "solar_irradiance_kwh_m2_day": round(solar, 2),
            "avg_temp_c": round(avg_temp, 1),
            "max_temp_c": round(avg_temp + 8, 1),
            "min_temp_c": round(avg_temp - 8, 1),
            "humidity_pct": round(max(30, min(90, humidity)), 1),
            "wind_speed_m_s": round(wind, 1),
            "evaporation_mm_day": round(evap, 2),
        })
    
    return pd.DataFrame(months)

def main():
    print("Generating Realistic Climate Data for Indian Dams...")
    print("=" * 70)
    
    input_data = Path("input_data")
    updated_count = 0
    
    for dam_name, base_solar in REGIONAL_SOLAR.items():
        dam_folder = input_data / dam_name
        
        if not dam_folder.exists():
            print(f"[SKIP] {dam_name.upper(): <20} - folder not found")
            continue
        
        base_temp = REGIONAL_TEMP.get(dam_name, 20)
        base_wind = WIND_BY_REGION.get(dam_name, 2.0)
        
        # Generate data
        df = create_climate_data(dam_name, base_solar, base_temp, base_wind)
        
        # Save to CSV
        climate_file = dam_folder / "climate.csv"
        df.to_csv(climate_file, index=False)
        
        print(f"[OK] {dam_name.upper(): <20} | Solar: {base_solar:.1f} kWh/m2/day | "
              f"Temp: {base_temp:.0f}C | Wind: {base_wind:.1f} m/s")
        
        updated_count += 1
    
    print("=" * 70)
    print(f"DONE: Generated climate data for {updated_count} dams!")
    print("Note: Reload React app or restart backend to see updated data")

if __name__ == "__main__":
    main()
