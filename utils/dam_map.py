"""
Interactive India Map with Dam Markers for FPV Nexus Dashboard
Shows all 43+ major Indian dams as clickable dots
Click a dam -> Load and analyze it
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import json
from pathlib import Path

def load_dams_index():
    """Load dams.json index"""
    try:
        with open("input_data/dams.json", "r") as f:
            return json.load(f)
    except:
        return {"dams": []}

def create_india_map():
    """Create interactive map of India with dam markers"""
    
    # Load dams data
    dams_data = load_dams_index()
    dams = dams_data.get("dams", [])
    
    if not dams:
        st.error("No dams found. Run: python generate_multi_dams.py")
        return None
    
    # Center of India
    india_center = [20.5937, 78.9629]
    
    # Create map
    m = folium.Map(
        location=india_center,
        zoom_start=5,
        tiles="OpenStreetMap"
    )
    
    # Add markers for each dam
    for dam in dams:
        lat = dam.get("latitude")
        lon = dam.get("longitude")
        name = dam.get("name", "Unknown")
        capacity = dam.get("capacity_mw", 0)
        state = dam.get("state", "")
        
        if lat and lon:
            # Color code by capacity
            if capacity > 1000:
                color = "red"  # Major
                icon_text = "MAJOR"
            elif capacity > 200:
                color = "orange"  # Medium
                icon_text = "MED"
            else:
                color = "blue"  # Small
                icon_text = "SML"
            
            # Popup info
            popup_text = f"""
            <b>{name}</b><br>
            Capacity: {capacity} MW<br>
            State: {state}<br>
            <a href="?dam={name}" target="_blank">View Analysis</a>
            """
            
            # Add marker
            folium.CircleMarker(
                location=[lat, lon],
                radius=8,
                popup=folium.Popup(popup_text, max_width=250),
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
                weight=2,
                tooltip=f"{name} ({capacity} MW)"
            ).add_to(m)
    
    return m, dams

def show_dam_map_selector():
    """Display interactive dam map in sidebar"""
    
    st.sidebar.markdown("## [MAP] India's Major Dams")
    st.sidebar.markdown("---")
    
    # Load dams
    dams_data = load_dams_index()
    dams = dams_data.get("dams", [])
    
    # Stats
    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        st.metric("Total", len(dams))
    with col2:
        major = sum(1 for d in dams if d.get("capacity_mw", 0) > 1000)
        st.metric("Major", major)
    with col3:
        complete = dams_data.get("complete", 0)
        st.metric("With Data", complete)
    
    st.sidebar.markdown("---")
    
    # Sort by capacity
    dams_sorted = sorted(dams, key=lambda x: x.get("capacity_mw", 0), reverse=True)
    
    # Select dam
    dam_options = {d["name"]: d for d in dams_sorted}
    selected_dam_name = st.sidebar.selectbox(
        "Select Dam",
        list(dam_options.keys()),
        format_func=lambda x: f"{x} ({dam_options[x].get('capacity_mw', 0)} MW)"
    )
    
    return dam_options[selected_dam_name] if selected_dam_name else None

def get_dam_analysis_page():
    """Render the full dam map in main area"""
    
    st.markdown("# [MAP] Interactive India Dam Selector")
    st.markdown("Click on any red/orange/blue dot to analyze that dam with FPV")
    
    try:
        m, dams = create_india_map()
        if m:
            map_data = st_folium(m, width=1400, height=600)
            
            st.markdown("---")
            
            # Dam stats table
            st.subheader("All 43+ Indian Dams in FPV Nexus")
            
            dams_df = pd.DataFrame(dams)
            dams_df = dams_df[["name", "state", "river", "capacity_mw", "area_km2", "head_m", "status"]]
            dams_df.columns = ["Dam Name", "State", "River", "Capacity (MW)", "Area (km2)", "Head (m)", "Status"]
            dams_df = dams_df.sort_values("Capacity (MW)", ascending=False)
            
            st.dataframe(dams_df, use_container_width=True, hide_index=True)
            
    except Exception as e:
        st.error(f"Error creating map: {str(e)}")

if __name__ == "__main__":
    get_dam_analysis_page()
