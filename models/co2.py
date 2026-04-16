"""
CO2 Emissions Avoidance Model
Computes environmental benefits of FPV + hydro system
"""

import numpy as np


def compute_co2_avoided_fpv(energy_mwh, grid_emission_factor=0.82):
    """
    Calculate CO2 avoided from FPV generation.
    
    Parameters:
    -----------
    energy_mwh : float
        FPV energy generation in MWh
    grid_emission_factor : float
        Grid emission factor in kg CO2/kWh (0.82 typical for India).
        Note: 0.82 kg/kWh is equivalent to 0.82 tCO2/MWh.
    
    Returns:
    --------
    dict
        Dictionary with 'tonnes' and 'kg'
    """
    co2_kg = energy_mwh * 1000 * grid_emission_factor  # MWh -> kWh
    co2_tonnes = co2_kg / 1000
    
    return {
        "kg": co2_kg,
        "tonnes": co2_tonnes
    }


def compute_co2_avoided_hydro(energy_mwh, grid_emission_factor=0.82):
    """
    Calculate CO2 avoided from additional hydro generation.
    
    Parameters:
    -----------
    energy_mwh : float
        Hydro energy in MWh
    grid_emission_factor : float
        Grid emission factor in kg CO2/kWh
    
    Returns:
    --------
    dict
        Dictionary with 'tonnes' and 'kg'
    """
    return compute_co2_avoided_fpv(energy_mwh, grid_emission_factor)


def compute_total_co2_avoided(fpv_energy_mwh, hydro_energy_mwh, grid_emission_factor=0.82):
    """
    Total CO2 avoidance from combined FPV + Hydro system.
    
    Parameters:
    -----------
    fpv_energy_mwh : float
        FPV energy in MWh
    hydro_energy_mwh : float
        Additional hydro energy in MWh
    grid_emission_factor : float
        Grid emission factor
    
    Returns:
    --------
    dict
        Total CO2 avoided in tonnes
    """
    total_energy = fpv_energy_mwh + hydro_energy_mwh
    co2_kg = total_energy * 1000 * grid_emission_factor
    co2_tonnes = co2_kg / 1000
    
    return {
        "total_kg": co2_kg,
        "total_tonnes": co2_tonnes,
        "fpv_tonnes": compute_co2_avoided_fpv(fpv_energy_mwh, grid_emission_factor)["tonnes"],
        "hydro_tonnes": compute_co2_avoided_hydro(hydro_energy_mwh, grid_emission_factor)["tonnes"]
    }


def compute_equivalent_trees(co2_tonnes, absorption_per_tree=0.025):
    """
    Calculate tree planting equivalent.
    
    Parameters:
    -----------
    co2_tonnes : float
        CO2 avoided in tonnes
    absorption_per_tree : float
        CO2 absorption per tree per year in tonnes (0.025 typical)
    
    Returns:
    --------
    float
        Number of equivalent trees
    """
    num_trees = co2_tonnes / absorption_per_tree if absorption_per_tree > 0 else 0
    
    return num_trees


def compute_equivalent_cars(co2_tonnes, emission_per_car=2.31):
    """
    Calculate equivalent cars removed from road.
    
    Parameters:
    -----------
    co2_tonnes : float
        CO2 avoided in tonnes
    emission_per_car : float
        Average car emission in tonnes CO2/year (2.31 typical)
    
    Returns:
    --------
    float
        Number of equivalent cars
    """
    num_cars = co2_tonnes / emission_per_car if emission_per_car > 0 else 0
    
    return num_cars


def compute_fuel_oil_equivalent(co2_tonnes, co2_per_liter_oil=2.35):
    """
    Calculate equivalent liters of fuel oil saved.
    
    Parameters:
    -----------
    co2_tonnes : float
        CO2 avoided in tonnes
    co2_per_liter_oil : float
        CO2 from 1 liter of fuel oil in kg (2.35 typical)
    
    Returns:
    --------
    float
        Equivalent liters of oil
    """
    co2_kg = co2_tonnes * 1000
    liters_oil = co2_kg / co2_per_liter_oil if co2_per_liter_oil > 0 else 0
    
    return liters_oil


def compute_sdg_impact(co2_tonnes, water_saved_million_m3):
    """
    Compute Sustainable Development Goals (SDG) alignment metrics.
    
    Parameters:
    -----------
    co2_tonnes : float
        CO2 avoided in tonnes
    water_saved_million_m3 : float
        Water saved in million m³
    
    Returns:
    --------
    dict
        SDG alignment metrics
    """
    return {
        "sdg_13_climate_action": co2_tonnes,  # Climate action
        "sdg_6_water": water_saved_million_m3 * 1e6 * 1000,  # Clean water (m3 → liters)
        "sdg_7_energy": "Renewable energy generation",  # Renewable energy
        "sdg_12_responsible": "Resource efficiency through water savings"  # Sustainable consumption
    }
