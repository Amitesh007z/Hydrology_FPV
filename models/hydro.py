"""
Hydropower Generation Model
Converts saved water to additional hydropower generation
"""

import numpy as np


def compute_extra_hydro_energy(volume_m3, head, efficiency=0.85, specific_gravity=1000):
    """
    Calculate additional hydropower energy from water savings.
    
    Parameters:
    -----------
    volume_m3 : float
        Water volume in m³
    head : float
        Hydro head in meters
    efficiency : float
        Turbine-generator efficiency (0.85 typical)
    specific_gravity : float
        Water specific gravity (1000 kg/m³)
    
    Returns:
    --------
    float
        Additional energy in MWh
    """
    # Gravitational potential energy: E = mgh
    g = 9.81  # m/s²
    mass = volume_m3 * specific_gravity  # kg
    
    # Energy in Joules
    energy_joules = mass * g * head * efficiency
    
    # Convert to MWh (1 MWh = 3.6 × 10^9 J)
    energy_mwh = energy_joules / 3.6e9
    
    return energy_mwh


def compute_hydro_power_output(flow_rate_m3_s, head, efficiency=0.85):
    """
    Calculate instantaneous hydropower output.
    
    Parameters:
    -----------
    flow_rate_m3_s : float
        Flow rate in m³/s
    head : float
        Hydro head in meters
    efficiency : float
        Turbine efficiency
    
    Returns:
    --------
    float
        Power output in MW
    """
    g = 9.81
    specific_gravity = 1000
    
    # Power = flow * head * gravity * efficiency
    power_watts = flow_rate_m3_s * specific_gravity * g * head * efficiency
    
    # Convert to MW
    power_mw = power_watts / 1e6
    
    return power_mw


def compute_hydro_capacity_factor(annual_mwh, installed_capacity_mw):
    """
    Calculate capacity factor of hydro plant.
    
    Parameters:
    -----------
    annual_mwh : float
        Annual energy generation in MWh
    installed_capacity_mw : float
        Installed capacity in MW
    
    Returns:
    --------
    float
        Capacity factor (0-1)
    """
    hours_per_year = 365 * 24
    potential_mwh = installed_capacity_mw * hours_per_year
    
    cf = annual_mwh / potential_mwh if potential_mwh > 0 else 0
    
    return min(cf, 1.0)


def compute_revenue_from_hydro(energy_mwh, tariff_per_mwh=4.5):
    """
    Estimate revenue from additional hydro generation.
    
    Parameters:
    -----------
    energy_mwh : float
        Energy in MWh
    tariff_per_mwh : float
        Average tariff in INR/MWh (4.5 INR typical)
    
    Returns:
    --------
    float
        Annual revenue in million INR
    """
    revenue_inr = energy_mwh * tariff_per_mwh
    revenue_million_inr = revenue_inr / 1e6
    
    return revenue_million_inr


def estimate_payback_period(capital_investment_crores, annual_revenue_crores):
    """
    Estimate payback period for FPV + water savings.
    
    Parameters:
    -----------
    capital_investment_crores : float
        CAPEX in crores INR
    annual_revenue_crores : float
        Annual net revenue in crores INR
    
    Returns:
    --------
    float
        Payback period in years
    """
    if annual_revenue_crores <= 0:
        return float('inf')
    
    payback_years = capital_investment_crores / annual_revenue_crores
    
    return payback_years
