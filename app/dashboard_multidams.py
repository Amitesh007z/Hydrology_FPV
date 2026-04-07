"""
FPV Nexus Dashboard v3.0 - Multi-Dam Interactive System
Floating Solar-Hydro Co-Optimization with India Map Selector
"""

import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import json
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
    st.error(f"Failed to import modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="FPV Nexus Dashboard v3.0",
    page_icon="SUN_ICON",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# Tab 1: Interactive Map Selector
# ============================================================================

def show_map_selector():
    """Display interactive India map with all dams"""
    
    st.markdown("# [MAP] India's 43+ Major Dams - FPV Analysis")
    st.markdown("Click on any dam marker or select from list below to analyze with Floating Solar")
    
    # Load dams
    try:
        with open("input_data/dams.json", "r") as f:
            dams_data = json.load(f)
            dams = dams_data.get("dams", [])
    except:
        st.error("Run: python generate_multi_dams.py")
        return
    
    if not dams:
        st.warning("No dams found. Generating...")
        return
    
    # Map columns
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Create interactive map
        india_center = [20.5937, 78.9629]
        m = folium.Map(location=india_center, zoom_start=5, tiles="OpenStreetMap")
        
        # Add markers
        for dam in dams:
            lat = dam.get("latitude")
            lon = dam.get("longitude")
            name = dam.get("name", "Unknown")
            capacity = dam.get("capacity_mw", 0)
            state = dam.get("state", "")
            
            if lat and lon:
                # Color by capacity
                if capacity > 1000:
                    color = "red"
                elif capacity > 200:
                    color = "orange"
                else:
                    color = "blue"
                
                popup_text = f"<b>{name}</b><br>Capacity: {capacity} MW<br>State: {state}"
                
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=8,
                    popup=popup_text,
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.7,
                    weight=2,
                    tooltip=f"{name} ({capacity} MW)"
                ).add_to(m)
        
        st_folium(m, width=1000, height=600)
    
    with col2:
        st.markdown("### Legend")
        st.markdown("🔴 **Major** (>1000 MW)")
        st.markdown("🟠 **Medium** (>200 MW)")
        st.markdown("🔵 **Small** (<200 MW)")
        
        st.markdown("### Stats")
        st.metric("Total", len(dams))
        st.metric("With Data", dams_data.get("complete", 0))
        
    # Dam selector
    st.markdown("---")
    st.markdown("### Select Dam to Analyze")
    
    dams_sorted = sorted(dams, key=lambda x: x.get("capacity_mw", 0), reverse=True)
    dam_dict = {f"{d['name']} ({d['capacity_mw']} MW)": d for d in dams_sorted}
    
    selected_dam_display = st.selectbox("", list(dam_dict.keys()))
    selected_dam = dam_dict[selected_dam_display]
    
    if st.button("Analyze Selected Dam", type="primary", use_container_width=True):
        st.session_state.selected_dam = selected_dam
        st.session_state.page = "analysis"
        st.rerun()
    
    # Display all dams table
    st.markdown("---")
    st.markdown("### All Dams Database")
    dams_df = pd.DataFrame(dams)
    dams_df = dams_df[["name", "state", "capacity_mw", "area_km2", "head_m", "status"]]
    dams_df.columns = ["Dam", "State", "MW", "Area (km2)", "Head (m)", "Status"]
    dams_df = dams_df.sort_values("MW", ascending=False)
    
    st.dataframe(dams_df, use_container_width=True, hide_index=True)


def show_dam_analysis():
    """Analyze selected dam with FPV"""
    
    dam = st.session_state.get("selected_dam")
    
    if not dam:
        st.warning("No dam selected. Go to Map tab.")
        return
    
    # Load dam real data
    try:
        reservoir_folder = Path(f"input_data/{dam['folder']}")
        real_data = load_real_reservoir(reservoir_folder)
        real_climate_df = load_real_climate(reservoir_folder)
        
        area_km2 = real_data["area_km2"]
        head_m = real_data["head_m"]
        installed_capacity_mw = real_data["installed_capacity_mw"]
        using_real_data = True
        
        # Process climate data
        monthly_data = real_climate_df.copy()
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
        
    except Exception as e:
        st.error(f"Error loading dam data: {str(e)}")
        return
    
    # Header
    st.markdown(f"# Analysis: {real_data['reservoir_name']}")
    st.markdown(f"**Location:** {real_data['latitude']}N, {real_data['longitude']}E | **River:** {real_data['river']} | **State:** {real_data['state']}")
    
    # Back button
    if st.button("< Back to Map"):
        st.session_state.page = "map"
        st.rerun()
    
    # Sidebar parameters
    st.sidebar.markdown("### FPV Parameters")
    coverage = st.sidebar.slider("FPV Coverage (%)", 1, 50, 10) / 100
    efficiency = st.sidebar.slider("Panel Efficiency", 0.10, 0.25, 0.18, step=0.01)
    pr = st.sidebar.slider("Performance Ratio", 0.60, 0.85, 0.75, step=0.01)
    
    structure_type = st.sidebar.radio(
        "FPV Structure",
        ["Pontoon (Rigid)", "Flexible Float"],
        help="Pontoon: 75% shading, Flexible: 57% shading"
    )
    structure_key = "pontoon" if "Pontoon" in structure_type else "flexible"
    shading_factor = compute_structure_shading_factor(structure_key)
    
    # Climate parameters
    annual_avg = compute_annual_averages(monthly_data)
    avg_irradiance = annual_avg["avg_solar_irradiance"]
    avg_evaporation = annual_avg["avg_evaporation"]
    avg_temp = annual_avg.get("avg_temp", 28.0)
    wind_speed = monthly_data["wind_speed"].mean() if "wind_speed" in monthly_data.columns else 3.0
    humidity = monthly_data["humidity"].mean() if "humidity" in monthly_data.columns else 65.0
    
    # ============================================================================
    #CALCULATIONS
    # ============================================================================
    
    area_m2 = area_km2 * 1e6
    effective_area_m2 = area_m2 * coverage
    
    cell_temp = compute_cell_temperature(avg_irradiance * 1000, avg_temp, wind_speed)
    temp_coeff_loss = compute_temp_coefficient_loss(cell_temp, ref_temp=25, temp_coeff=-0.004)
    
    daily_fpv_mwh = compute_fpv_power(area_km2, coverage, avg_irradiance, efficiency, pr, temp_coeff_loss)
    annual_fpv_mwh = compute_annual_fpv_energy(daily_fpv_mwh, days=365)
    fpv_capacity_mwp = compute_fpv_capacity(area_km2, coverage, efficiency)
    
    water_saved_million_m3 = compute_evaporation_reduction_volume(
        effective_area_m2, avg_evaporation, shading_factor=shading_factor, variation=1.0
    )
    
    hydro_efficiency = 0.85
    extra_hydro_mwh_annual = compute_extra_hydro_energy(
        water_saved_million_m3 * 1e6, head_m, efficiency=hydro_efficiency
    )
    
    total_energy_mwh = annual_fpv_mwh + extra_hydro_mwh_annual
    
    co2_result = compute_total_co2_avoided(annual_fpv_mwh, extra_hydro_mwh_annual, 0.82)
    co2_tonnes = co2_result["total_tonnes"]
    
    trees = compute_equivalent_trees(co2_tonnes, 0.025)
    cars = compute_equivalent_cars(co2_tonnes, 2.31)
    
    # Financial
    capex_cr_per_mwp = 4.0
    fpv_tariff = 3.5
    hydro_tariff = 4.5
    discount_rate = 0.10
    project_lifetime = 25
    
    financial = compute_full_financial_analysis(
        fpv_capacity_mwp, annual_fpv_mwh, extra_hydro_mwh_annual, co2_tonnes,
        capex_cr_per_mwp=capex_cr_per_mwp, opex_percent=0.02,
        fpv_tariff=fpv_tariff, hydro_tariff=hydro_tariff,
        discount_rate=discount_rate, lifetime_years=project_lifetime
    )
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("FPV Capacity", f"{fpv_capacity_mwp:.1f} MWp", f"{coverage*100:.1f}%")
    with col2:
        st.metric("Water Saved", f"{water_saved_million_m3:.2f}M m3", f"Structures: {structure_key}")
    with col3:
        st.metric("Extra Hydro", f"{extra_hydro_mwh_annual:.0f} MWh", "Annual")
    with col4:
        st.metric("CO2 Avoided", f"{co2_tonnes:,.0f} t", "Annual")
    
    # Results
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"""
        ### Energy Generation
        - **FPV:** {annual_fpv_mwh:,.0f} MWh/year
        - **Hydro:** {extra_hydro_mwh_annual:,.0f} MWh/year
        - **Total:** {total_energy_mwh:,.0f} MWh/year
        """)
    with col2:
        payback_str = f"{financial['payback']['payback_years']:.1f} yrs" if financial['payback']['payback_years'] < 100 else "N/A"
        st.info(f"""
        ### Financial
        - **CAPEX:** Rs.{financial['capex_total_cr']:.2f} Cr
        - **LCOE:** Rs.{financial['lcoe']['lcoe_inr_per_kwh']:.2f}/kWh
        - **Payback:** {payback_str}
        - **ROI:** {financial['roi']['roi_percent']:.1f}%
        """)


# ============================================================================
# MAIN APP
# ============================================================================

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "map"

if "selected_dam" not in st.session_state:
    st.session_state.selected_dam = None

# Navigation
if st.session_state.page == "map":
    show_map_selector()
else:
    show_dam_analysis()
