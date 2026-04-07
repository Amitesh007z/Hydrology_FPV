"""
Evaporation Reduction Model
Computes water savings from floating solar shading effect
"""

import numpy as np


def compute_evaporation_reduction_volume(area_m2, evap_mm_per_day, shading_factor=0.7, variation=1.0):
    """
    Calculate water volume saved due to evaporation reduction.
    
    Parameters:
    -----------
    area_m2 : float
        Surface area covered by FPV in m²
    evap_mm_per_day : float
        Daily evaporation rate in mm/day
    shading_factor : float
        Shading effectiveness (0.7 typical = 70% reduction)
    variation : float
        Climate variation multiplier (1.0 = normal, 1.1 = +10%)
    
    Returns:
    --------
    float
        Annual water savings in million m³
    """
    # Annual evaporation with variation
    annual_mm = evap_mm_per_day * 365 * variation
    
    # Water volume saved with shading factor
    volume_m3 = area_m2 * (annual_mm / 1000) * shading_factor
    
    # Convert to million m³
    volume_million_m3 = volume_m3 / 1e6
    
    return volume_million_m3


def compute_water_savings_liters(area_m2, evap_mm_per_day, shading_factor=0.7, variation=1.0):
    """
    Water savings in liters (daily).
    
    Parameters:
    -----------
    area_m2 : float
        FPV covered area in m²
    evap_mm_per_day : float
        Daily evaporation in mm
    shading_factor : float
        Shading factor
    variation : float
        Climate variation
    
    Returns:
    --------
    float
        Daily water savings in million liters
    """
    # Daily reduction in mm (evaporation)
    daily_reduction_mm = evap_mm_per_day * shading_factor * variation
    
    # Convert to volume: area * depth
    # 1 mm = 1 liter/m²
    daily_liters = area_m2 * daily_reduction_mm
    
    # Convert to million liters
    daily_million_liters = daily_liters / 1e6
    
    return daily_million_liters


def compute_seasonal_variation(base_evap, season="summer"):
    """
    Apply seasonal variation to evaporation rates.
    
    Parameters:
    -----------
    base_evap : float
        Base evaporation rate (mm/day)
    season : str
        'summer', 'monsoon', 'winter'
    
    Returns:
    --------
    float
        Adjusted evaporation rate
    """
    seasonal_factors = {
        "summer": 1.4,  # +40%
        "monsoon": 0.6,  # -40%
        "winter": 0.8   # -20%
    }
    
    factor = seasonal_factors.get(season, 1.0)
    return base_evap * factor


def compute_uncertainty_range(volume_million_m3, uncertainty_percent=15):
    """
    Compute uncertainty range for water savings.
    
    Parameters:
    -----------
    volume_million_m3 : float
        Base volume calculation
    uncertainty_percent : float
        Uncertainty margin (%)
    
    Returns:
    --------
    dict
        Dictionary with 'low', 'mid', 'high' estimates
    """
    uncertainty = volume_million_m3 * (uncertainty_percent / 100)
    
    return {
        "low": volume_million_m3 - uncertainty,
        "mid": volume_million_m3,
        "high": volume_million_m3 + uncertainty
    }


def compute_regression_evaporation(solar_rad_mj, temp_c, humidity_pct, wind_speed_m_s):
    """
    Multi-variable regression-based evaporation model from research literature.

    E = a0 + a1*Rs + a2*Ta - a3*RH + a4*u10

    Parameters
    ----------
    solar_rad_mj : float
        Incoming solar radiation in MJ/m²/day
    temp_c : float
        Air temperature in °C
    humidity_pct : float
        Relative humidity in %
    wind_speed_m_s : float
        Wind speed at 10m height in m/s

    Returns
    -------
    float
        Estimated daily evaporation in mm/day
    """
    # Regression coefficients (derived from Indian reservoir studies)
    a0 = 0.5
    a1 = 0.15   # solar radiation contribution
    a2 = 0.08   # temperature contribution
    a3 = 0.02   # humidity suppresses evaporation
    a4 = 0.12   # wind enhances evaporation

    evap_mm = a0 + a1 * solar_rad_mj + a2 * temp_c - a3 * humidity_pct + a4 * wind_speed_m_s

    # Clamp to realistic range
    return max(evap_mm, 0.5)


def compute_structure_shading_factor(structure_type="pontoon"):
    """
    Return the shading factor based on FPV structure type.

    Parameters
    ----------
    structure_type : str
        "pontoon" (rigid, higher coverage) or "flexible" (lighter, lower shading)

    Returns
    -------
    float
        Shading factor (0-1)
    """
    factors = {
        "pontoon": 0.75,    # Rigid pontoon: 70-80% evaporation reduction
        "flexible": 0.57,   # Flexible float: 50-65% evaporation reduction
    }
    return factors.get(structure_type.lower(), 0.70)
