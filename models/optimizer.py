"""
Smart Optimizer for FPV Nexus
Finds optimal FPV coverage based on selected optimization mode.
Uses brute-force search over coverage range — no external solver needed.
"""

import numpy as np


def _run_scenario(area_km2, coverage, head_m, irradiance, evaporation,
                  efficiency=0.18, pr=0.75, shading_factor=0.70,
                  capex_cr_per_mwp=4.0, fpv_tariff=3.5, hydro_tariff=4.5,
                  emission_factor=0.82):
    """
    Run a single scenario and return key metrics.
    Inlined computation to avoid circular imports.
    """
    # Area
    area_m2 = area_km2 * 1e6
    effective_area_m2 = area_m2 * coverage

    # FPV Capacity (MWp)
    capacity_mwp = effective_area_m2 * efficiency / 1e6

    # Daily energy (MWh/day) — simplified (no temp correction for speed)
    daily_mwh = effective_area_m2 * irradiance * efficiency * pr / 1000
    annual_fpv_mwh = daily_mwh * 365

    # Water saved (million m³)
    annual_evap_m = evaporation * 365 / 1000
    water_saved_m3 = effective_area_m2 * annual_evap_m * shading_factor
    water_saved_million = water_saved_m3 / 1e6

    # Extra hydro (MWh)
    g = 9.81
    hydro_mwh = water_saved_m3 * 1000 * g * head_m * 0.85 / 3.6e9

    # Total energy
    total_mwh = annual_fpv_mwh + hydro_mwh

    # CO₂ avoided (tonnes)
    co2_tonnes = total_mwh * emission_factor

    # Financial (tariffs in ₹/kWh → ×1000 for MWh, then ÷1e7 for Crores)
    capex_cr = capacity_mwp * capex_cr_per_mwp
    opex_cr = capex_cr * 0.02
    fpv_revenue_cr = (annual_fpv_mwh * fpv_tariff * 1000) / 1e7
    hydro_revenue_cr = (hydro_mwh * hydro_tariff * 1000) / 1e7
    total_revenue_cr = fpv_revenue_cr + hydro_revenue_cr
    net_annual_cr = total_revenue_cr - opex_cr
    payback = capex_cr / net_annual_cr if net_annual_cr > 0 else float('inf')
    roi = ((total_revenue_cr * 25 - capex_cr - opex_cr * 25) / capex_cr * 100) if capex_cr > 0 else 0

    return {
        "coverage_pct": round(coverage * 100, 1),
        "capacity_mwp": round(capacity_mwp, 2),
        "annual_fpv_mwh": round(annual_fpv_mwh, 0),
        "water_saved_million_m3": round(water_saved_million, 2),
        "hydro_mwh": round(hydro_mwh, 0),
        "total_energy_mwh": round(total_mwh, 0),
        "co2_tonnes": round(co2_tonnes, 0),
        "capex_cr": round(capex_cr, 2),
        "payback_years": round(payback, 1),
        "roi_percent": round(roi, 1),
        "net_annual_revenue_cr": round(net_annual_cr, 4),
    }


def optimize_scenario(area_km2, head_m, irradiance, evaporation,
                      mode="max_energy", max_coverage=0.10,
                      efficiency=0.18, pr=0.75, shading_factor=0.70,
                      capex_cr_per_mwp=4.0, fpv_tariff=3.5, hydro_tariff=4.5,
                      emission_factor=0.82, steps=100):
    """
    Find optimal FPV coverage percentage for the given optimization mode.

    Parameters
    ----------
    area_km2 : float
        Reservoir area in km²
    head_m : float
        Hydraulic head in meters
    irradiance : float
        Average solar irradiance (kWh/m²/day)
    evaporation : float
        Average evaporation rate (mm/day)
    mode : str
        Optimization mode: "max_energy", "best_roi", or "water_priority"
    max_coverage : float
        Maximum allowed coverage (0.10 = 10%, ecological constraint)
    efficiency : float
        Panel efficiency
    pr : float
        Performance ratio
    shading_factor : float
        Shading factor for evaporation reduction
    capex_cr_per_mwp : float
        CAPEX per MWp in ₹ Crores
    fpv_tariff : float
        FPV energy tariff ₹/MWh
    hydro_tariff : float
        Hydro energy tariff ₹/MWh
    emission_factor : float
        Grid emission factor (kg CO₂/kWh)
    steps : int
        Number of coverage steps to evaluate

    Returns
    -------
    dict
        Optimal scenario with recommendation
    """
    coverages = np.linspace(0.01, max_coverage, steps)
    results = []

    for cov in coverages:
        scenario = _run_scenario(
            area_km2, cov, head_m, irradiance, evaporation,
            efficiency, pr, shading_factor,
            capex_cr_per_mwp, fpv_tariff, hydro_tariff, emission_factor
        )
        results.append(scenario)

    # Select best based on mode
    if mode == "max_energy":
        best = max(results, key=lambda x: x["total_energy_mwh"])
        reason = "Maximizes total energy output (FPV + Hydro)"
    elif mode == "best_roi":
        best = max(results, key=lambda x: x["roi_percent"])
        reason = "Maximizes Return on Investment over 25-year lifetime"
    elif mode == "water_priority":
        best = max(results, key=lambda x: x["water_saved_million_m3"])
        reason = "Maximizes water savings from evaporation reduction"
    else:
        best = max(results, key=lambda x: x["total_energy_mwh"])
        reason = "Default: maximizes total energy output"

    return {
        "mode": mode,
        "reason": reason,
        "optimal": best,
        "max_coverage_pct": max_coverage * 100,
    }


def compare_scenarios(area_km2, head_m, irradiance, evaporation,
                      coverages=None, **kwargs):
    """
    Generate side-by-side comparison of multiple coverage scenarios.

    Parameters
    ----------
    area_km2 : float
        Reservoir area
    head_m : float
        Hydraulic head
    irradiance : float
        Solar irradiance
    evaporation : float
        Evaporation rate
    coverages : list
        Coverage fractions to compare (default: [0.05, 0.10, 0.15])

    Returns
    -------
    list
        List of scenario result dicts
    """
    if coverages is None:
        coverages = [0.05, 0.10, 0.15]

    scenarios = []
    for cov in coverages:
        result = _run_scenario(area_km2, cov, head_m, irradiance, evaporation, **kwargs)
        scenarios.append(result)

    return scenarios
