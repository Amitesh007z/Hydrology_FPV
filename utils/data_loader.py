"""
Data Loader Utility v2.0
Load and preprocess reservoir and climate data
Supports: input_data/ folder for real data + built-in defaults
"""

import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================================
# INPUT DATA DISCOVERY
# ============================================================================

def get_input_data_dir():
    """Get the input_data directory path."""
    project_root = Path(__file__).parent.parent
    return project_root / "input_data"


def discover_reservoirs():
    """
    Auto-discover all reservoir datasets in input_data/ folder.

    Returns
    -------
    dict
        {reservoir_name: folder_path} for each discovered dataset
    """
    input_dir = get_input_data_dir()
    reservoirs = {}

    if input_dir.exists():
        for folder in sorted(input_dir.iterdir()):
            if folder.is_dir() and (folder / "reservoir.csv").exists():
                # Use folder name as reservoir key, title-cased
                name = folder.name.replace("_", " ").title()
                reservoirs[name] = folder

    return reservoirs


# ============================================================================
# REAL DATA LOADERS
# ============================================================================

def load_real_reservoir(folder_path):
    """
    Load reservoir data from a real dataset folder.

    Parameters
    ----------
    folder_path : Path
        Path to the reservoir folder (e.g., input_data/srisailam/)

    Returns
    -------
    dict
        Reservoir parameters
    """
    csv_path = Path(folder_path) / "reservoir.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        record = df.to_dict("records")[0]
        return {
            "reservoir_name": record.get("reservoir_name", "Unknown"),
            "state": record.get("state", ""),
            "river": record.get("river", ""),
            "latitude": float(record.get("latitude", 0)),
            "longitude": float(record.get("longitude", 0)),
            "area_km2": float(record.get("area_km2", 50)),
            "gross_storage_mcm": float(record.get("gross_storage_mcm", 500)),
            "live_storage_mcm": float(record.get("live_storage_mcm", 300)),
            "frl_m": float(record.get("frl_m", 100)),
            "mddl_m": float(record.get("mddl_m", 80)),
            "head_m": float(record.get("head_m", 25)),
            "installed_capacity_mw": float(record.get("installed_capacity_mw", 100)),
            "turbine_type": record.get("turbine_type", "Francis"),
            "turbine_efficiency": float(record.get("turbine_efficiency", 0.85)),
            "num_units": int(record.get("num_units", 1)),
        }
    return load_reservoir_data()


def load_real_climate(folder_path):
    """
    Load monthly climate data from a real dataset folder.

    Parameters
    ----------
    folder_path : Path
        Path to the reservoir folder

    Returns
    -------
    pd.DataFrame
        Monthly climate data with standardized column names
    """
    csv_path = Path(folder_path) / "climate.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        # Standardize column names
        rename_map = {}
        for col in df.columns:
            col_lower = col.lower()
            if "solar" in col_lower or "irradiance" in col_lower:
                rename_map[col] = "solar_irradiance"
            elif "avg_temp" in col_lower or col_lower == "t2m":
                rename_map[col] = "avg_temp"
            elif "max_temp" in col_lower:
                rename_map[col] = "max_temp"
            elif "min_temp" in col_lower:
                rename_map[col] = "min_temp"
            elif "humid" in col_lower:
                rename_map[col] = "humidity"
            elif "wind" in col_lower:
                rename_map[col] = "wind_speed"
            elif "evap" in col_lower:
                rename_map[col] = "evaporation"

        df = df.rename(columns=rename_map)
        return df
    return get_monthly_climate_data()


# ============================================================================
# BUILT-IN DEFAULT DATA (unchanged from v1.0)
# ============================================================================

def load_reservoir_data(filepath=None):
    """
    Load reservoir data from CSV or return defaults.
    """
    if filepath and Path(filepath).exists():
        df = pd.read_csv(filepath)
        return df.to_dict('records')[0]

    return {
        "reservoir_name": "Sample Reservoir",
        "area_km2": 50.0,
        "storage_capacity_mcm": 500.0,
        "head_m": 25.0,
        "installed_capacity_mw": 100.0,
        "turbine_efficiency": 0.85,
        "min_water_level": 100.0,
        "max_water_level": 120.0
    }


def load_climate_data(filepath=None):
    """
    Load climate data from CSV or return defaults.
    """
    if filepath and Path(filepath).exists():
        df = pd.read_csv(filepath)
        return df.to_dict('records')[0]

    return {
        "month": "January",
        "avg_temp_c": 25.0,
        "solar_irradiance_kwh_m2_day": 4.5,
        "evaporation_mm_day": 3.5,
        "wind_speed_m_s": 2.0,
        "humidity_percent": 65.0
    }


def get_monthly_climate_data():
    """
    Get typical monthly climate data for India (built-in default).
    """
    months = [
        {"month": "January", "avg_temp": 22, "solar_irradiance": 4.2, "evaporation": 2.5},
        {"month": "February", "avg_temp": 25, "solar_irradiance": 4.8, "evaporation": 2.8},
        {"month": "March", "avg_temp": 30, "solar_irradiance": 5.5, "evaporation": 3.5},
        {"month": "April", "avg_temp": 33, "solar_irradiance": 5.8, "evaporation": 4.2},
        {"month": "May", "avg_temp": 35, "solar_irradiance": 5.5, "evaporation": 4.5},
        {"month": "June", "avg_temp": 32, "solar_irradiance": 4.2, "evaporation": 3.8},
        {"month": "July", "avg_temp": 30, "solar_irradiance": 3.8, "evaporation": 3.2},
        {"month": "August", "avg_temp": 29, "solar_irradiance": 4.1, "evaporation": 3.1},
        {"month": "September", "avg_temp": 28, "solar_irradiance": 4.5, "evaporation": 3.0},
        {"month": "October", "avg_temp": 27, "solar_irradiance": 5.0, "evaporation": 2.8},
        {"month": "November", "avg_temp": 24, "solar_irradiance": 4.8, "evaporation": 2.5},
        {"month": "December", "avg_temp": 21, "solar_irradiance": 4.1, "evaporation": 2.3},
    ]
    return pd.DataFrame(months)


def compute_annual_averages(monthly_data):
    """
    Compute annual averages from monthly data.
    """
    result = {}

    if "avg_temp" in monthly_data.columns:
        result["avg_temp"] = monthly_data["avg_temp"].mean()
    if "solar_irradiance" in monthly_data.columns:
        result["avg_solar_irradiance"] = monthly_data["solar_irradiance"].mean()
        result["total_solar_irradiance"] = monthly_data["solar_irradiance"].sum()
    if "evaporation" in monthly_data.columns:
        result["avg_evaporation"] = monthly_data["evaporation"].mean()
    if "humidity" in monthly_data.columns:
        result["avg_humidity"] = monthly_data["humidity"].mean()
    if "wind_speed" in monthly_data.columns:
        result["avg_wind_speed"] = monthly_data["wind_speed"].mean()

    return result


def normalize_units(value, unit_from, unit_to):
    """
    Normalize units for consistency.
    """
    area_conversions = {
        ("km2", "m2"): lambda x: x * 1e6,
        ("m2", "km2"): lambda x: x / 1e6,
        ("hectare", "m2"): lambda x: x * 10000,
        ("m2", "hectare"): lambda x: x / 10000,
    }

    volume_conversions = {
        ("m3", "million_m3"): lambda x: x / 1e6,
        ("million_m3", "m3"): lambda x: x * 1e6,
        ("mcm", "m3"): lambda x: x * 1e6,
        ("m3", "mcm"): lambda x: x / 1e6,
    }

    key = (unit_from, unit_to)

    if key in area_conversions:
        return area_conversions[key](value)
    elif key in volume_conversions:
        return volume_conversions[key](value)
    else:
        return value
