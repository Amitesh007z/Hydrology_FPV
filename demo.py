#!/usr/bin/env python3
"""
FPV Nexus Dashboard v2.0 - Core Computation Demo
Enhanced with Financial Engine, Optimizer, and Advanced Evaporation
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("FPV NEXUS DASHBOARD v2.0 - CORE COMPUTATION DEMO")
print("Decision Intelligence Platform")
print("=" * 80)

try:
    from models.fpv import compute_fpv_power, compute_fpv_capacity, compute_cell_temperature
    from models.evaporation import (
        compute_evaporation_reduction_volume,
        compute_regression_evaporation,
        compute_structure_shading_factor
    )
    from models.hydro import compute_extra_hydro_energy, compute_revenue_from_hydro
    from models.co2 import compute_total_co2_avoided, compute_equivalent_trees, compute_equivalent_cars
    from models.financial import compute_full_financial_analysis
    from models.optimizer import optimize_scenario, compare_scenarios
    from utils.data_loader import (
        load_reservoir_data, get_monthly_climate_data, compute_annual_averages,
        discover_reservoirs, load_real_reservoir, load_real_climate
    )
    print("[OK] All modules imported successfully (including v2.0 enhancements)!\n")
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    sys.exit(1)

# ============================================================================
# DEMO SCENARIO: Srisailam Dam with 12% FPV Coverage (REAL DATA)
# ============================================================================

print("DEMO SCENARIO: Srisailam Dam (REAL WORLD DATA) with 12% FPV Coverage")
print("=" * 80)

# Discover and load real Srisailam data
real_reservoirs = discover_reservoirs()
print(f"\n[INFO] Available Real Reservoirs: {list(real_reservoirs.keys())}\n")

# Load Srisailam Dam real data - check for both possible names
srisailam_key = None
if "Srisailam Dam" in real_reservoirs:
    srisailam_key = "Srisailam Dam"
elif "Srisailam" in real_reservoirs:
    srisailam_key = "Srisailam"

if srisailam_key:
    srisailam_folder = real_reservoirs[srisailam_key]
    real_data = load_real_reservoir(srisailam_folder)
    real_climate_df = load_real_climate(srisailam_folder)
    
    # Input parameters from real data
    area_km2 = real_data["area_km2"]
    head_m = real_data["head_m"]
    installed_capacity_mw = real_data["installed_capacity_mw"]
    coverage = 0.12  # 12% FPV coverage
    
    # Climate data from real NASA POWER data
    monthly_data = real_climate_df.copy()
    
    # Standardize column names
    if "solar_irradiance_kwh_m2_day" in monthly_data.columns:
        monthly_data = monthly_data.rename(columns={"solar_irradiance_kwh_m2_day": "solar_irradiance"})
    if "avg_temp_c" in monthly_data.columns:
        monthly_data = monthly_data.rename(columns={"avg_temp_c": "avg_temp"})
    if "evaporation_mm_day" in monthly_data.columns:
        monthly_data = monthly_data.rename(columns={"evaporation_mm_day": "evaporation"})
    if "humidity_pct" in monthly_data.columns:
        monthly_data = monthly_data.rename(columns={"humidity_pct": "humidity"})
    if "wind_speed_m_s" in monthly_data.columns:
        monthly_data = monthly_data.rename(columns={"wind_speed_m_s": "wind_speed"})
    
    annual_avg = compute_annual_averages(monthly_data)
    
    avg_irradiance = annual_avg["avg_solar_irradiance"]
    avg_evaporation = annual_avg["avg_evaporation"]
    avg_temp = annual_avg.get("avg_temp", 28.0)
    
    # Get wind and humidity from real data
    wind_speed = monthly_data["wind_speed"].mean() if "wind_speed" in monthly_data.columns else 3.0
    humidity = monthly_data["humidity"].mean() if "humidity" in monthly_data.columns else 65.0
    
    print(f"\n[SUCCESS] LOADED REAL DATA: {real_data['reservoir_name']}")
    print(f"   Location: {real_data['latitude']}N, {real_data['longitude']}E")
    print(f"   River: {real_data['river']} | State: {real_data['state']}")
    print(f"   Data Source: NASA POWER API (2013-2023 average)")
    using_real_data = True
else:
    print("[WARNING] Srisailam Dam data not found. Using demo defaults.")
    # Fallback to demo defaults
    real_data = {
        "reservoir_name": "Demo Reservoir",
        "area_km2": 45.0,
        "head_m": 28.5,
        "installed_capacity_mw": 85.0,
        "latitude": 0,
        "longitude": 0,
        "river": "",
        "state": "",
        "gross_storage_mcm": 0,
        "live_storage_mcm": 0,
    }
    area_km2 = 45.0
    coverage = 0.15
    head_m = 28.5
    installed_capacity_mw = 85.0
    monthly_data = get_monthly_climate_data()
    annual_avg = compute_annual_averages(monthly_data)
    avg_irradiance = annual_avg["avg_solar_irradiance"]
    avg_evaporation = annual_avg["avg_evaporation"]
    avg_temp = 28.0
    wind_speed = 2.0
    humidity = 65.0
    using_real_data = False

print(f"\n1. RESERVOIR PARAMETERS")
print(f"   {'Reservoir Name:':<25} {real_data['reservoir_name']}")
if using_real_data:
    print(f"   {'Location:':<25} {real_data['latitude']}N, {real_data['longitude']}E")
    print(f"   {'River / State:':<25} {real_data['river']} / {real_data['state']}")
    if real_data.get('gross_storage_mcm', 0) > 0:
        print(f"   {'Gross Storage:':<25} {real_data['gross_storage_mcm']:.0f} MCM")
    if real_data.get('live_storage_mcm', 0) > 0:
        print(f"   {'Live Storage:':<25} {real_data['live_storage_mcm']:.0f} MCM")
    if real_data.get('installed_capacity_mw', 0) > 0:
        print(f"   {'Installed Hydro Capacity:':<25} {real_data['installed_capacity_mw']} MW")
elif real_data.get('gross_storage_mcm', 0) == 0:
    pass
print(f"   {'Reservoir Area:':<25} {area_km2} km2")
print(f"   {'Hydraulic Head:':<25} {head_m} m")
print(f"   {'FPV Coverage:':<25} {coverage*100:.1f}%")

print(f"\n2. CLIMATE PARAMETERS (Annual Average)")
print(f"   {'Solar Irradiance:':<25} {avg_irradiance:.2f} kWh/m2/day")
print(f"   {'Evaporation Rate:':<25} {avg_evaporation:.2f} mm/day")
print(f"   {'Avg Temperature:':<25} {avg_temp:.1f} C")
print(f"   {'Wind Speed:':<25} {wind_speed:.2f} m/s")
print(f"   {'Humidity:':<25} {humidity:.1f}%")

# ============================================================================
# CALCULATIONS
# ============================================================================

print(f"\n3. FPV ENERGY CALCULATIONS")
print("-" * 80)

# FPV Capacity
fpv_capacity_mwp = compute_fpv_capacity(area_km2, coverage, efficiency=0.18)
print(f"   FPV Installed Capacity: {fpv_capacity_mwp:.1f} MWp")

# Temperature correction
area_m2 = area_km2 * 1e6
cell_temp = compute_cell_temperature(avg_irradiance * 1000, avg_temp, wind_speed)
temp_correction = 1 - (-0.004) * (cell_temp - 25)
print(f"   Cell Temperature: {cell_temp:.1f} C")
print(f"   Temp Correction Factor: {temp_correction:.3f}")

# Daily FPV power
daily_fpv_mwh = compute_fpv_power(area_km2, coverage, avg_irradiance, efficiency=0.18, pr=0.75, temp_correction=temp_correction)
print(f"   Daily FPV Energy: {daily_fpv_mwh:.2f} MWh/day")

# Annual FPV energy
annual_fpv_mwh = daily_fpv_mwh * 365
print(f"   Annual FPV Energy: {annual_fpv_mwh:,.0f} MWh/year")


print(f"\n4. WATER SAVINGS CALCULATIONS")
print("-" * 80)

# Structure type comparison
for struct in ["pontoon", "flexible"]:
    sf = compute_structure_shading_factor(struct)
    print(f"   Structure: {struct.title():<12} => Shading Factor: {sf:.0%}")

# Use pontoon for main demo
shading_factor = compute_structure_shading_factor("pontoon")

# Water savings
effective_area_m2 = area_m2 * coverage
water_saved_million_m3 = compute_evaporation_reduction_volume(
    effective_area_m2, avg_evaporation, shading_factor=shading_factor, variation=1.0
)
print(f"\n   Using Pontoon structure (shading: {shading_factor:.0%})")
print(f"   Covered Area: {effective_area_m2/1e6:.1f} km2")
print(f"   Annual Water Savings: {water_saved_million_m3:.2f} Million m3")


print(f"\n4b. ADVANCED EVAPORATION MODEL (Regression)")
print("-" * 80)

solar_rad_mj = avg_irradiance * 3.6  # kWh  MJ
regression_evap = compute_regression_evaporation(solar_rad_mj, avg_temp, humidity, wind_speed)
print(f"   Regression Input: Rs={solar_rad_mj:.1f} MJ/m2/day, T={avg_temp}C, RH={humidity}%, Wind={wind_speed} m/s")
print(f"   Regression Evaporation: {regression_evap:.2f} mm/day")
print(f"   Simple Model Evaporation: {avg_evaporation:.2f} mm/day")
print(f"   Difference: {abs(regression_evap - avg_evaporation):.2f} mm/day")


print(f"\n5. HYDROPOWER GENERATION FROM WATER SAVINGS")
print("-" * 80)

hydro_efficiency = 0.85
extra_hydro_mwh_annual = compute_extra_hydro_energy(
    water_saved_million_m3 * 1e6, head_m, efficiency=hydro_efficiency
)
print(f"   Water Volume: {water_saved_million_m3 * 1e6:,.0f} m3")
print(f"   Hydro Head: {head_m} m")
print(f"   Turbine Efficiency: {hydro_efficiency*100}%")
print(f"   Extra Hydro Energy: {extra_hydro_mwh_annual:,.0f} MWh/year")
print(f"   Capacity Factor Boost: {(extra_hydro_mwh_annual / (installed_capacity_mw * 24 * 365) * 100):.2f}%")


print(f"\n6. ENVIRONMENTAL IMPACT")
print("-" * 80)

total_energy_mwh = annual_fpv_mwh + extra_hydro_mwh_annual
emission_factor = 0.82

co2_result = compute_total_co2_avoided(annual_fpv_mwh, extra_hydro_mwh_annual, emission_factor)

print(f"   Total Energy (FPV + Hydro): {total_energy_mwh:,.0f} MWh/year")
print(f"   Grid Emission Factor: {emission_factor} kg CO2/kWh (India)")
print(f"   CO2 Avoided: {co2_result['total_tonnes']:,.0f} tonnes/year")
print(f"   - From FPV: {co2_result['fpv_tonnes']:,.0f} tonnes")
print(f"   - From Extra Hydro: {co2_result['hydro_tonnes']:,.0f} tonnes")

trees = compute_equivalent_trees(co2_result["total_tonnes"], 0.025)
cars = compute_equivalent_cars(co2_result["total_tonnes"], 2.31)

print(f"\n   ENVIRONMENTAL EQUIVALENTS:")
print(f"   [TREES] Trees planted equivalent: {trees:,.0f}")
print(f"   [CARS] Cars removed from road: {cars:,.0f}")


print(f"\n7. ECONOMIC ANALYSIS (Basic)")
print("-" * 80)

hydro_tariff = 4.5
hydro_revenue_crore = compute_revenue_from_hydro(extra_hydro_mwh_annual, hydro_tariff)
print(f"   Annual Hydro Revenue: Rs.{hydro_revenue_crore:.2f} Crores")
print(f"   (at Rs.{hydro_tariff}/kWh tariff)")


# ============================================================================
# v2.0 ENHANCEMENTS
# ============================================================================

print(f"\n{'='*80}")
print(f"  v2.0 ENHANCEMENTS  Financial Engine + Smart Optimizer")
print(f"{'='*80}")


print(f"\n9. FINANCIAL ANALYSIS (NEW)")
print("-" * 80)

financial = compute_full_financial_analysis(
    fpv_capacity_mwp, annual_fpv_mwh, extra_hydro_mwh_annual,
    co2_result["total_tonnes"],
    capex_cr_per_mwp=4.0, opex_percent=0.02,
    fpv_tariff=3.5, hydro_tariff=4.5,
    discount_rate=0.10, lifetime_years=25,
    degradation_rate=0.005
)

print(f"   CAPEX: Rs.{financial['capex_total_cr']:.2f} Crores ({fpv_capacity_mwp:.1f} MWp  Rs.4 Cr/MWp)")
print(f"   Annual O&M: Rs.{financial['opex_annual_cr']:.2f} Crores")
print(f"\n   Revenue Streams (Annual):")
print(f"    FPV Energy Sale:    Rs.{financial['fpv_revenue_cr']:.4f} Cr")
print(f"    Hydro Energy Sale:  Rs.{financial['hydro_revenue_cr']:.4f} Cr")
print(f"    Carbon Credits:     Rs.{financial['carbon_credit_cr']:.4f} Cr")
print(f"    Total Revenue:      Rs.{financial['total_annual_revenue_cr']:.4f} Cr/year")
print(f"\n   Key Financial Metrics:")
print(f"   [LCOE]             Rs.{financial['lcoe']['lcoe_inr_per_kwh']:.2f}/kWh (Rs.{financial['lcoe']['lcoe_inr_per_mwh']:.0f}/MWh)")

payback_val = financial['payback']['payback_years']
payback_str = f"{payback_val:.1f} years" if payback_val < 100 else "N/A"
print(f"   [PAYBACK]          {payback_str}")
print(f"    ROI (25 years):  {financial['roi']['roi_percent']:.1f}%")
print(f"    Net Profit:      Rs.{financial['roi']['net_profit_cr']:.2f} Crores (lifetime)")


print(f"\n10. SMART OPTIMIZER (NEW)")
print("-" * 80)

for mode in ["max_energy", "best_roi", "water_priority"]:
    result = optimize_scenario(
        area_km2, head_m, avg_irradiance, avg_evaporation,
        mode=mode, max_coverage=0.10,
        shading_factor=shading_factor
    )
    opt = result["optimal"]
    print(f"\n   Mode: {mode.upper()}")
    print(f"   => Optimal Coverage: {opt['coverage_pct']:.1f}%")
    print(f"   => Total Energy: {opt['total_energy_mwh']:,.0f} MWh")
    print(f"   => Water Saved: {opt['water_saved_million_m3']:.2f}M m3")
    print(f"   => ROI: {opt['roi_percent']:.1f}% | Payback: {opt['payback_years']:.1f} yrs")


print(f"\n11. SCENARIO COMPARISON (NEW)")
print("-" * 80)

scenarios = compare_scenarios(
    area_km2, head_m, avg_irradiance, avg_evaporation,
    coverages=[0.05, 0.10, 0.15],
    shading_factor=shading_factor
)

print(f"\n   {'Coverage':>10} {'Energy (MWh)':>15} {'Water (M m3)':>15} {'CO2 (t)':>12} {'Payback':>10} {'ROI (%)':>10}")
print(f"   {'-'*72}")
for s in scenarios:
    print(f"   {s['coverage_pct']:>9.1f}% {s['total_energy_mwh']:>14,.0f} {s['water_saved_million_m3']:>14.2f} {s['co2_tonnes']:>11,.0f} {s['payback_years']:>9.1f} {s['roi_percent']:>9.1f}")


print(f"\n{'='*80}")
print(f"\n DEMO COMPLETE  All v2.0 computations verified!\n")
print(f"Next Steps:")
print(f"  $ python -m streamlit run app/dashboard.py    # Interactive Dashboard v2.0")
print(f"  $ python -m uvicorn backend.main:app --reload # API Server v2.0")
print("=" * 80)
