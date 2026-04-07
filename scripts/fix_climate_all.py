"""
Scan all input_data/*/climate.csv files and replace zero/empty climate values
with realistic monthly estimates. Only fills fields that are zero or missing.
"""
from pathlib import Path
import pandas as pd
import math

INPUT_DIR = Path(__file__).resolve().parents[1] / "input_data"

# Fallback and regional defaults (kWh/m2/day)
REGIONAL_SOLAR = {
    "talakaveri": 4.5,
    "koyna": 4.8,
    "srisailam": 5.2,
    "bhakra_nangal": 4.2,
    "tehri": 4.0,
    "indira_sagar": 5.1,
    "sardar_sarovar": 5.3,
    "nagarjuna_sagar": 5.0,
}
FALLBACK_SOLAR = 4.5

SOLAR_SEASONALITY = [0.7, 0.75, 0.85, 0.95, 1.0, 0.95, 0.85, 0.8, 0.9, 0.95, 0.7, 0.65]
MONTH_NAMES = ["January","February","March","April","May","June","July","August","September","October","November","December"]

REGIONAL_TEMP = {
    "talakaveri": 22,
    "koyna": 21,
    "srisailam": 25,
    "bhakra_nangal": 15,
    "tehri": 14,
    "indira_sagar": 24,
    "sardar_sarovar": 26,
    "nagarjuna_sagar": 25,
}

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


def generate_monthly(base_solar, base_temp, base_wind):
    rows = []
    for i, m in enumerate(MONTH_NAMES):
        solar = round(base_solar * SOLAR_SEASONALITY[i], 2)
        temp_variation = 8 * math.sin((i - 2) * math.pi / 6)
        avg_temp = round(base_temp + temp_variation, 1)
        max_temp = round(avg_temp + 8, 1)
        min_temp = round(avg_temp - 8, 1)
        wind = round(base_wind * (0.8 + 0.4 * SOLAR_SEASONALITY[i]), 1)
        humidity = round(max(30, min(90, 65 - (avg_temp - base_temp) * 0.5)), 1)
        evap = round((solar / 3) + 0.5, 2)
        rows.append({
            "month": m,
            "solar_irradiance_kwh_m2_day": solar,
            "avg_temp_c": avg_temp,
            "max_temp_c": max_temp,
            "min_temp_c": min_temp,
            "humidity_pct": humidity,
            "wind_speed_m_s": wind,
            "evaporation_mm_day": evap,
        })
    return pd.DataFrame(rows)


def is_zero_or_missing_series(s):
    return s.isnull().all() or (s.fillna(0) == 0).all()


def fix_file(path: Path):
    try:
        df = pd.read_csv(path)
    except Exception as e:
        print(f"[ERR] {path} read: {e}")
        return False

    # Columns we expect
    cols = ["month","solar_irradiance_kwh_m2_day","avg_temp_c","max_temp_c","min_temp_c","humidity_pct","wind_speed_m_s","evaporation_mm_day"]
    for c in cols:
        if c not in df.columns:
            df[c] = pd.NA

    # Determine if solar data is invalid (all zeros or missing)
    solar_bad = is_zero_or_missing_series(df['solar_irradiance_kwh_m2_day'])

    # Also check if other key fields mostly zero
    temp_bad = is_zero_or_missing_series(df['avg_temp_c'])
    wind_bad = is_zero_or_missing_series(df['wind_speed_m_s'])
    evap_bad = is_zero_or_missing_series(df['evaporation_mm_day'])

    if not (solar_bad or temp_bad or wind_bad or evap_bad):
        # nothing to do
        return False

    name = path.parent.name.lower()
    base_solar = REGIONAL_SOLAR.get(name, FALLBACK_SOLAR)
    base_temp = REGIONAL_TEMP.get(name, 20)
    base_wind = WIND_BY_REGION.get(name, 2.0)

    print(f"[FIX] {path.parent.name} - filling missing climate data (solar={base_solar}, temp={base_temp}, wind={base_wind})")
    newdf = generate_monthly(base_solar, base_temp, base_wind)

    # Replace only zero/missing cells in original df
    out = df.copy()
    for col in newdf.columns:
        if col == 'month':
            out['month'] = newdf['month']
            continue
        # mask where original is null or zero
        mask = out[col].isnull() | (out[col] == 0)
        out.loc[mask, col] = newdf.loc[mask, col]

    # Ensure correct order and types
    out = out[cols]
    out.to_csv(path, index=False)
    return True


def main():
    files = list(INPUT_DIR.glob("*/climate.csv"))
    updated = 0
    for f in files:
        if fix_file(f):
            updated += 1
    print(f"Done. Updated {updated}/{len(files)} climate files.")

if __name__ == '__main__':
    main()
