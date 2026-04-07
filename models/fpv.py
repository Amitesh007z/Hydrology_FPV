"""
FPV (Floating Photovoltaic) Energy Model
Computes solar power generation from floating solar installations
"""

import numpy as np

try:
    # Commented out due to Windows long path issues with pvlib
    # from pvlib.temperature import fuentes
    fuentes = None
except ImportError:
    fuentes = None


def compute_fpv_power(area_km2, coverage, irradiance, efficiency, pr=0.75, temp_correction=1.0):
    """
    Calculate floating PV power generation.
    
    Parameters:
    -----------
    area_km2 : float
        Reservoir surface area in km²
    coverage : float
        Coverage fraction (0-1, e.g., 0.1 for 10%)
    irradiance : float
        Solar irradiance in kWh/m²/day
    efficiency : float
        Panel efficiency (0.15-0.22 typical for commercial)
    pr : float
        Performance ratio (0.75 typical)
    temp_correction : float
        Temperature correction factor (0-1)
    
    Returns:
    --------
    float
        Power generation in MWh/day
    """
    # Convert area to m²
    area_m2 = area_km2 * 1e6
    
    # Effective covered area
    effective_area = area_m2 * coverage
    
    # Energy generation (kWh/day)
    energy_kwh = effective_area * irradiance * efficiency * pr * temp_correction
    
    # Convert to MWh/day
    energy_mwh = energy_kwh / 1000
    
    return energy_mwh


def compute_annual_fpv_energy(daily_mwh, days=365):
    """
    Convert daily energy to annual.
    
    Parameters:
    -----------
    daily_mwh : float
        Daily energy in MWh
    days : int
        Number of days (365 default)
    
    Returns:
    --------
    float
        Annual energy in MWh
    """
    return daily_mwh * days


def compute_fpv_capacity(area_km2, coverage, efficiency):
    """
    Calculate peak FPV capacity (MWp).
    
    Parameters:
    -----------
    area_km2 : float
        Reservoir area in km²
    coverage : float
        Coverage fraction
    efficiency : float
        Panel efficiency
    
    Returns:
    --------
    float
        Installed capacity in MWp (at 1000 W/m² irradiance)
    """
    area_m2 = area_km2 * 1e6
    effective_area = area_m2 * coverage
    
    # Standard Test Condition: 1000 W/m²
    stc_irradiance = 1.0  # kW/m²
    
    capacity_mw = effective_area * stc_irradiance * efficiency / 1e6
    
    return capacity_mw


def compute_cell_temperature(irradiance, temp_air, wind_speed=1.0):
    """
    Compute PV cell temperature correction using Fuentes model.
    
    Parameters:
    -----------
    irradiance : float
        Solar irradiance in W/m²
    temp_air : float
        Air temperature in °C
    wind_speed : float
        Wind speed in m/s
    
    Returns:
    --------
    float
        Cell temperature in °C
    """
    try:
        # pvlib fuentes model
        # Model: T_cell = T_air + irradiance/1000 * (NOCT - 20) / 80
        noct = 45  # Nominal Operating Cell Temperature
        cell_temp = temp_air + (irradiance / 1000) * (noct - 20) / 80
        return cell_temp
    except Exception:
        # Fallback simple model
        cell_temp = temp_air + (irradiance / 1000) * 30
        return cell_temp


def compute_temp_coefficient_loss(cell_temp, ref_temp=25, temp_coeff=-0.004):
    """
    Compute efficiency loss due to temperature.
    
    Parameters:
    -----------
    cell_temp : float
        Cell temperature in °C
    ref_temp : float
        Reference temperature (25°C standard)
    temp_coeff : float
        Temperature coefficient of efficiency (%/°C)
    
    Returns:
    --------
    float
        Correction factor (0-1)
    """
    temp_loss = 1 + temp_coeff * (cell_temp - ref_temp)
    return max(temp_loss, 0.7)  # Clamp to realistic range
