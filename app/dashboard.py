"""
FPV Nexus Dashboard v2.0 - Enhanced Streamlit Application
Floating Solar-Hydro Co-Optimization System
Includes: Financial Engine, Smart Optimizer, Scenario Comparison
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# Import computation modules
try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from models import (
        compute_fpv_power, compute_annual_fpv_energy, compute_fpv_capacity,
        compute_cell_temperature, compute_temp_coefficient_loss,
        compute_evaporation_reduction_volume,
        compute_regression_evaporation, compute_structure_shading_factor,
        compute_extra_hydro_energy,
        compute_total_co2_avoided, compute_equivalent_trees, compute_equivalent_cars,
        compute_full_financial_analysis, FINANCIAL_DEFAULTS,
        optimize_scenario, compare_scenarios
    )
    from utils import (
        load_reservoir_data, get_monthly_climate_data, compute_annual_averages,
        discover_reservoirs, load_real_reservoir, load_real_climate
    )
except ImportError as e:
    st.error(f"❌ Failed to import modules: {e}")
    st.stop()


# Page configuration
st.set_page_config(
    page_title="FPV Nexus Dashboard v2.0",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .header-title {
        color: #1f77b4;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .subheader {
        color: #555;
        font-size: 1.2em;
        margin-bottom: 20px;
    }
    .financial-highlight {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# SIDEBAR - INPUT PARAMETERS
# ============================================================================

st.sidebar.markdown("# ⚙️ FPV Configuration")

# Auto-discover real reservoir datasets from input_data/
real_reservoirs = discover_reservoirs()
real_names = [f"📊 {name} (Real Data)" for name in real_reservoirs.keys()]

# Built-in presets
builtin_presets = {
    "Bhaira Reservoir": {"area_km2": 45.0, "head_m": 28.5, "installed_capacity_mw": 85.0},
    "Rana Pratap Sagar": {"area_km2": 89.5, "head_m": 32.0, "installed_capacity_mw": 115.0},
    "Indira Sagar": {"area_km2": 245.0, "head_m": 58.0, "installed_capacity_mw": 1000.0},
    "Koyna Reservoir": {"area_km2": 56.8, "head_m": 48.0, "installed_capacity_mw": 1960.0},
}

# Combine: Real Data reservoirs first, then presets, then Custom
all_options = real_names + list(builtin_presets.keys()) + ["Custom"]
reservoir_name = st.sidebar.selectbox("Select Reservoir", all_options)

# Determine data source
using_real_data = False
real_climate_df = None

if reservoir_name.startswith("📊"):
    # Real data reservoir
    clean_name = reservoir_name.replace("📊 ", "").replace(" (Real Data)", "")
    folder = real_reservoirs[clean_name]
    real_data = load_real_reservoir(folder)
    area_km2 = real_data["area_km2"]
    head_m = real_data["head_m"]
    installed_capacity_mw = real_data["installed_capacity_mw"]
    reservoir_name = real_data["reservoir_name"]
    using_real_data = True
    real_climate_df = load_real_climate(folder)
    st.sidebar.success(f"✅ Using REAL data for **{reservoir_name}**\n\n"
                       f"📍 {real_data.get('latitude', '?')}°N, {real_data.get('longitude', '?')}°E\n\n"
                       f"🏗️ {real_data.get('river', '')} | {real_data.get('state', '')}")
elif reservoir_name == "Custom":
    area_km2 = st.sidebar.number_input("Reservoir Area (km²)", min_value=1.0, max_value=1000.0, value=50.0)
    head_m = st.sidebar.number_input("Hydro Head (m)", min_value=5.0, max_value=200.0, value=25.0)
    installed_capacity_mw = st.sidebar.number_input("Installed Capacity (MW)", min_value=10.0, max_value=5000.0, value=100.0)
else:
    data = builtin_presets[reservoir_name]
    area_km2 = data["area_km2"]
    head_m = data["head_m"]
    installed_capacity_mw = data["installed_capacity_mw"]

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 FPV Parameters")

coverage = st.sidebar.slider("FPV Coverage (%)", 1, 50, 10) / 100
efficiency = st.sidebar.slider("Panel Efficiency", 0.10, 0.25, 0.18, step=0.01)
pr = st.sidebar.slider("Performance Ratio", 0.60, 0.85, 0.75, step=0.01)

# NEW: Structure Type
st.sidebar.markdown("---")
st.sidebar.markdown("### 🏗️ Structure Type")
structure_type = st.sidebar.radio(
    "FPV Structure",
    ["Pontoon (Rigid)", "Flexible Float"],
    help="Pontoon: higher shading (75%), Flexible: lighter but lower shading (57%)"
)
structure_key = "pontoon" if "Pontoon" in structure_type else "flexible"
shading_factor = compute_structure_shading_factor(structure_key)
st.sidebar.caption(f"Shading Factor: **{shading_factor:.0%}**")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🌦️ Climate Parameters")

# Use real climate data if available, otherwise use defaults
if using_real_data and real_climate_df is not None:
    monthly_data = real_climate_df.copy()
    # Standardize column names to ensure compatibility
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
    st.sidebar.info("📊 Using **REAL CLIMATE DATA** from NASA POWER API")
else:
    monthly_data = get_monthly_climate_data()

annual_avg = compute_annual_averages(monthly_data)

avg_irradiance = st.sidebar.slider(
    "Solar Irradiance (kWh/m²/day)",
    2.0, 6.0,
    float(annual_avg["avg_solar_irradiance"]),
    step=0.1
)

# NEW: Evaporation model toggle
evap_model = st.sidebar.radio("Evaporation Model", ["Simple", "Advanced (Regression)"])

avg_evaporation = st.sidebar.slider(
    "Evaporation Rate (mm/day)",
    1.0, 6.0,
    float(annual_avg["avg_evaporation"]),
    step=0.1
)

temp_variation = st.sidebar.slider(
    "Evaporation Variation",
    0.8, 1.2, 1.0, step=0.05
)

wind_speed = st.sidebar.slider("Wind Speed (m/s)", 0.5, 5.0, 2.0, step=0.1)
avg_temp = st.sidebar.slider("Average Temperature (°C)", 15.0, 40.0, 28.0, step=1.0)
humidity = st.sidebar.slider("Humidity (%)", 30.0, 90.0, 65.0, step=5.0)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💰 Economic Parameters")

emission_factor = st.sidebar.slider(
    "Grid Emission Factor (kg CO₂/MWh)",
    0.5, 1.2, 0.82, step=0.01
)

hydro_tariff = st.sidebar.slider(
    "Hydro Tariff (₹/MWh)",
    2.0, 6.0, 4.5, step=0.1
)

# NEW: Financial parameters
st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Financial Parameters")

capex_cr_per_mwp = st.sidebar.slider(
    "CAPEX (₹ Cr/MWp)", 3.0, 6.0, 4.0, step=0.5
)
fpv_tariff = st.sidebar.slider(
    "FPV Tariff (₹/MWh)", 2.0, 5.0, 3.5, step=0.1
)
discount_rate = st.sidebar.slider(
    "Discount Rate (%)", 6, 15, 10
) / 100
project_lifetime = st.sidebar.slider(
    "Project Lifetime (years)", 20, 30, 25
)


# ============================================================================
# MAIN CONTENT - HEADER
# ============================================================================

st.markdown(f"<div class='header-title'>☀️ FPV NEXUS DASHBOARD v2.0</div>", unsafe_allow_html=True)
st.markdown(f"<div class='subheader'>Decision Intelligence Platform — Floating Solar-Hydro Co-Optimization</div>", unsafe_allow_html=True)

st.markdown(f"**Reservoir:** {reservoir_name} | **Area:** {area_km2} km² | **Head:** {head_m} m | **Structure:** {structure_type}",
            unsafe_allow_html=True)

# ============================================================================
# CALCULATIONS
# ============================================================================

# 1. FPV Power Generation
area_m2 = area_km2 * 1e6
effective_area_m2 = area_m2 * coverage

# Temperature correction
cell_temp = compute_cell_temperature(avg_irradiance * 1000, avg_temp, wind_speed)
temp_coeff_loss = compute_temp_coefficient_loss(cell_temp, ref_temp=25, temp_coeff=-0.004)

# Daily FPV power
daily_fpv_mwh = compute_fpv_power(
    area_km2, coverage, avg_irradiance, efficiency, pr, temp_coeff_loss
)

# Annual FPV energy
annual_fpv_mwh = compute_annual_fpv_energy(daily_fpv_mwh, days=365)

# FPV capacity
fpv_capacity_mwp = compute_fpv_capacity(area_km2, coverage, efficiency)

# 2. Evaporation Reduction & Water Savings
if evap_model == "Advanced (Regression)":
    # Convert irradiance kWh/m²/day → MJ/m²/day (1 kWh = 3.6 MJ)
    solar_rad_mj = avg_irradiance * 3.6
    computed_evap = compute_regression_evaporation(solar_rad_mj, avg_temp, humidity, wind_speed)
    evaporation_used = computed_evap
else:
    evaporation_used = avg_evaporation

water_saved_million_m3 = compute_evaporation_reduction_volume(
    effective_area_m2, evaporation_used, shading_factor=shading_factor, variation=temp_variation
)

# 3. Extra Hydro Energy
hydro_efficiency = 0.85
extra_hydro_mwh_annual = compute_extra_hydro_energy(
    water_saved_million_m3 * 1e6, head_m, efficiency=hydro_efficiency
)

# 4. Total Energy & CO2
total_energy_mwh = annual_fpv_mwh + extra_hydro_mwh_annual

co2_result = compute_total_co2_avoided(
    annual_fpv_mwh, extra_hydro_mwh_annual, emission_factor
)

co2_tonnes = co2_result["total_tonnes"]

# Environmental equivalents
trees = compute_equivalent_trees(co2_tonnes, absorption_per_tree=0.025)
cars = compute_equivalent_cars(co2_tonnes, emission_per_car=2.31)

# 5. Financial Analysis
financial = compute_full_financial_analysis(
    fpv_capacity_mwp, annual_fpv_mwh, extra_hydro_mwh_annual, co2_tonnes,
    capex_cr_per_mwp=capex_cr_per_mwp, opex_percent=0.02,
    fpv_tariff=fpv_tariff, hydro_tariff=hydro_tariff,
    discount_rate=discount_rate, lifetime_years=project_lifetime,
    degradation_rate=0.005
)

# ============================================================================
# KEY METRICS (KPIs)
# ============================================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "🔆 FPV Capacity",
        f"{fpv_capacity_mwp:.1f} MWp",
        f"Coverage: {coverage*100:.1f}%"
    )

with col2:
    st.metric(
        "💧 Water Saved",
        f"{water_saved_million_m3:.2f}M m³",
        f"Structure: {structure_key.title()}"
    )

with col3:
    st.metric(
        "⚡ Extra Hydro",
        f"{extra_hydro_mwh_annual:.0f} MWh",
        "Annual generation"
    )

with col4:
    st.metric(
        "🌍 CO₂ Avoided",
        f"{co2_tonnes:,.0f} tonnes",
        "Annual impact"
    )

# ============================================================================
# ENERGY OUTPUT SECTION
# ============================================================================

st.markdown("---")
st.markdown("## 📈 Energy Generation Analysis")

col1, col2 = st.columns(2)

with col1:
    st.info(f"""
    ### Daily Generation
    - 🌞 FPV: **{daily_fpv_mwh:.2f} MWh/day**
    - 📊 Temperature Effect: **{temp_coeff_loss*100:.1f}%**
    - 💧 Cell Temp: **{cell_temp:.1f}°C**
    - 🏗️ Evap Model: **{evap_model}** ({evaporation_used:.2f} mm/day)
    """)

with col2:
    st.success(f"""
    ### Annual Generation
    - ☀️ FPV Energy: **{annual_fpv_mwh:,.0f} MWh**
    - 💧 Hydro Energy: **{extra_hydro_mwh_annual:,.0f} MWh**
    - ⚡ Total Energy: **{total_energy_mwh:,.0f} MWh**
    """)

# Energy composition chart
energy_data = {
    "Source": ["FPV Solar", "Extra Hydro"],
    "Annual Energy (MWh)": [annual_fpv_mwh, extra_hydro_mwh_annual]
}

fig_energy = px.bar(
    energy_data,
    x="Source",
    y="Annual Energy (MWh)",
    title="Energy Contribution Mix",
    color="Source",
    color_discrete_map={"FPV Solar": "#FDB462", "Extra Hydro": "#80B1D3"}
)
fig_energy.update_layout(height=400, showlegend=False)

st.plotly_chart(fig_energy, use_container_width=True)

# ============================================================================
# 💰 FINANCIAL ANALYSIS SECTION (NEW)
# ============================================================================

st.markdown("---")
st.markdown("## 💰 Financial Analysis")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "📊 LCOE",
        f"₹{financial['lcoe']['lcoe_inr_per_kwh']:.2f}/kWh",
        f"₹{financial['lcoe']['lcoe_inr_per_mwh']:.0f}/MWh"
    )

with col2:
    payback_val = financial['payback']['payback_years']
    payback_display = f"{payback_val:.1f} yrs" if payback_val < 100 else "N/A"
    st.metric(
        "⏱️ Payback Period",
        payback_display,
        "With degradation"
    )

with col3:
    st.metric(
        "📈 ROI",
        f"{financial['roi']['roi_percent']:.1f}%",
        f"Over {project_lifetime} years"
    )

with col4:
    st.metric(
        "💵 CAPEX",
        f"₹{financial['capex_total_cr']:.1f} Cr",
        f"O&M: ₹{financial['opex_annual_cr']:.2f} Cr/yr"
    )

# Revenue breakdown
col1, col2 = st.columns(2)

with col1:
    st.info(f"""
    ### Revenue Streams (Annual)
    - ☀️ FPV Energy Sale: **₹{financial['fpv_revenue_cr']:.4f} Cr**
    - 💧 Hydro Energy Sale: **₹{financial['hydro_revenue_cr']:.4f} Cr**
    - 🌍 Carbon Credits: **₹{financial['carbon_credit_cr']:.4f} Cr**
    - 💰 **Total: ₹{financial['total_annual_revenue_cr']:.4f} Cr/year**
    """)

with col2:
    st.success(f"""
    ### Lifetime Economics ({project_lifetime} years)
    - 💵 Total Revenue: **₹{financial['roi']['total_revenue_cr']:.2f} Cr**
    - 💸 Total Cost: **₹{financial['roi']['total_cost_cr']:.2f} Cr**
    - 🎯 Net Profit: **₹{financial['roi']['net_profit_cr']:.2f} Cr**
    """)

# ============================================================================
# ENVIRONMENTAL IMPACT SECTION
# ============================================================================

st.markdown("---")
st.markdown("## 🌍 Environmental Impact")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🌳 Equivalent Trees",
        f"{trees:,.0f}",
        "Trees planted equivalent"
    )

with col2:
    st.metric(
        "🚗 Cars Offset",
        f"{cars:,.0f}",
        "Cars removed from road"
    )

with col3:
    st.metric(
        "💧 Water Saved",
        f"{water_saved_million_m3 * 1e9 / 1000:.0f}M liters",
        "Drinking water potential"
    )

# CO2 breakdown
fig_co2 = go.Figure(data=[
    go.Bar(name='FPV Solar', x=['CO₂ Avoided (tonnes)'], y=[co2_result["fpv_tonnes"]], marker_color='#FDB462'),
    go.Bar(name='Extra Hydro', x=['CO₂ Avoided (tonnes)'], y=[co2_result["hydro_tonnes"]], marker_color='#80B1D3')
])
fig_co2.update_layout(
    title="CO₂ Emissions Avoided (Annual)",
    barmode='stack',
    height=400
)

st.plotly_chart(fig_co2, use_container_width=True)

# ============================================================================
# 🎯 SMART OPTIMIZER (NEW)
# ============================================================================

st.markdown("---")
st.markdown("## 🎯 Smart Optimizer")

col1, col2 = st.columns([1, 2])

with col1:
    opt_mode = st.selectbox(
        "Optimization Goal",
        ["max_energy", "best_roi", "water_priority"],
        format_func=lambda x: {
            "max_energy": "⚡ Maximize Energy",
            "best_roi": "💰 Best ROI",
            "water_priority": "💧 Water Priority"
        }[x]
    )
    max_cov = st.slider("Max Coverage Constraint (%)", 5, 50, 10) / 100
    run_optimizer = st.button("🚀 Find Optimal Coverage", type="primary", use_container_width=True)

with col2:
    if run_optimizer:
        with st.spinner("Running optimization..."):
            result = optimize_scenario(
                area_km2, head_m, avg_irradiance, evaporation_used,
                mode=opt_mode, max_coverage=max_cov,
                efficiency=efficiency, pr=pr, shading_factor=shading_factor,
                capex_cr_per_mwp=capex_cr_per_mwp,
                fpv_tariff=fpv_tariff, hydro_tariff=hydro_tariff,
                emission_factor=emission_factor
            )

        opt = result["optimal"]
        st.success(f"""
        ### ✅ Optimization Result: **{opt['coverage_pct']:.1f}% Coverage**
        
        **Strategy:** {result['reason']}
        
        | Metric | Value |
        |--------|-------|
        | Capacity | {opt['capacity_mwp']:.1f} MWp |
        | Annual Energy | {opt['total_energy_mwh']:,.0f} MWh |
        | Water Saved | {opt['water_saved_million_m3']:.2f}M m³ |
        | CO₂ Avoided | {opt['co2_tonnes']:,.0f} tonnes |
        | Payback | {opt['payback_years']:.1f} years |
        | ROI | {opt['roi_percent']:.1f}% |
        """)
    else:
        st.info("👆 Select an optimization goal and click **Find Optimal Coverage** to get a recommendation.")

# ============================================================================
# 📊 SCENARIO COMPARISON (NEW)
# ============================================================================

st.markdown("---")
st.markdown("## 📊 Scenario Comparison")

scenarios = compare_scenarios(
    area_km2, head_m, avg_irradiance, evaporation_used,
    coverages=[0.05, 0.10, 0.15],
    efficiency=efficiency, pr=pr, shading_factor=shading_factor,
    capex_cr_per_mwp=capex_cr_per_mwp,
    fpv_tariff=fpv_tariff, hydro_tariff=hydro_tariff,
    emission_factor=emission_factor
)

comparison_df = pd.DataFrame(scenarios)
comparison_df = comparison_df.rename(columns={
    "coverage_pct": "Coverage (%)",
    "capacity_mwp": "Capacity (MWp)",
    "annual_fpv_mwh": "FPV Energy (MWh)",
    "water_saved_million_m3": "Water Saved (M m³)",
    "hydro_mwh": "Hydro Energy (MWh)",
    "total_energy_mwh": "Total Energy (MWh)",
    "co2_tonnes": "CO₂ Avoided (t)",
    "capex_cr": "CAPEX (₹Cr)",
    "payback_years": "Payback (yrs)",
    "roi_percent": "ROI (%)",
    "net_annual_revenue_cr": "Net Revenue (₹Cr/yr)"
})

st.dataframe(comparison_df, use_container_width=True, hide_index=True)

# ============================================================================
# SCENARIO SUMMARY TABLE
# ============================================================================

st.markdown("---")
st.markdown("## 📋 Current Scenario Summary")

summary_data = {
    "Parameter": [
        "Reservoir Area (km²)",
        "FPV Coverage (%)",
        "Panel Efficiency (%)",
        "Hydro Head (m)",
        "Structure Type",
        "Evaporation Model",
        "FPV Capacity (MWp)",
        "Annual FPV Energy (MWh)",
        "Water Saved (Million m³)",
        "Extra Hydro Energy (MWh)",
        "Total Energy (MWh)",
        "CO₂ Avoided (tonnes)",
        "LCOE (₹/kWh)",
        "Payback Period (years)",
        "ROI (%)",
        "CAPEX (₹ Crores)",
    ],
    "Value": [
        f"{area_km2:.1f}",
        f"{coverage*100:.1f}",
        f"{efficiency*100:.1f}",
        f"{head_m:.1f}",
        structure_type,
        evap_model,
        f"{fpv_capacity_mwp:.1f}",
        f"{annual_fpv_mwh:,.0f}",
        f"{water_saved_million_m3:.2f}",
        f"{extra_hydro_mwh_annual:,.0f}",
        f"{total_energy_mwh:,.0f}",
        f"{co2_tonnes:,.0f}",
        f"₹{financial['lcoe']['lcoe_inr_per_kwh']:.2f}",
        f"{financial['payback']['payback_years']:.1f}" if financial['payback']['payback_years'] < 100 else "N/A",
        f"{financial['roi']['roi_percent']:.1f}",
        f"₹{financial['capex_total_cr']:.2f}",
    ]
}

summary_df = pd.DataFrame(summary_data)
st.dataframe(summary_df, use_container_width=True, hide_index=True)

# ============================================================================
# MONTHLY BREAKDOWN
# ============================================================================

st.markdown("---")
st.markdown("## 📅 Monthly Breakdown (Sample)")

monthly_variations = monthly_data.copy()
# Ensure solar_irradiance column exists for calculation
if "solar_irradiance" in monthly_variations.columns:
    monthly_variations["FPV (MWh)"] = (daily_fpv_mwh * 30 * (monthly_variations["solar_irradiance"] / avg_irradiance)).round(0)
    display_cols = ["month", "solar_irradiance", "evaporation", "FPV (MWh)"]
    if "avg_temp" in monthly_variations.columns:
        display_cols.insert(2, "avg_temp")
    if "humidity" in monthly_variations.columns:
        display_cols.insert(3, "humidity")
    display_cols = [col for col in display_cols if col in monthly_variations.columns]
else:
    monthly_variations["FPV (MWh)"] = daily_fpv_mwh * 30
    display_cols = ["month", "FPV (MWh)"]

st.dataframe(
    monthly_variations[display_cols],
    use_container_width=True,
    hide_index=True
)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; font-size: 0.9em;'>
    <p>🔬 <strong>FPV Nexus Dashboard v2.0</strong> | Decision Intelligence Platform</p>
    <p>Floating Solar-Hydro Co-Optimization | Financial Engine | Smart Optimizer</p>
    <p>Data sources: NASA POWER, IMD, CEA India | Built with Streamlit & Plotly</p>
</div>
""", unsafe_allow_html=True)


# ============================================================================
# EXPORT FUNCTIONALITY
# ============================================================================

st.sidebar.markdown("---")
if st.sidebar.button("📥 Generate Report"):
    payback_str = f"{financial['payback']['payback_years']:.1f}" if financial['payback']['payback_years'] < 100 else "N/A"
    report = f"""
    # FPV Nexus Dashboard v2.0 - Scenario Report

    ## Configuration
    - Reservoir: {reservoir_name}
    - Area: {area_km2} km²
    - Coverage: {coverage*100:.1f}%
    - Structure: {structure_type}
    - Evaporation Model: {evap_model}

    ## Energy Results
    - FPV Capacity: {fpv_capacity_mwp:.1f} MWp
    - Annual FPV Energy: {annual_fpv_mwh:,.0f} MWh
    - Water Saved: {water_saved_million_m3:.2f} Million m³
    - Extra Hydro Energy: {extra_hydro_mwh_annual:,.0f} MWh
    - Total Energy: {total_energy_mwh:,.0f} MWh
    - CO₂ Avoided: {co2_tonnes:,.0f} tonnes

    ## Financial Results
    - CAPEX: ₹{financial['capex_total_cr']:.2f} Crores
    - LCOE: ₹{financial['lcoe']['lcoe_inr_per_kwh']:.2f}/kWh
    - Payback Period: {payback_str} years
    - ROI: {financial['roi']['roi_percent']:.1f}%
    - Net Profit (Lifetime): ₹{financial['roi']['net_profit_cr']:.2f} Crores
    """
    st.sidebar.download_button(
        label="📄 Download Report",
        data=report,
        file_name="fpv_report_v2.txt",
        mime="text/plain"
    )
