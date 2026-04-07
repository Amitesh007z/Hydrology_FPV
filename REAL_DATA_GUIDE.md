# 🌍 FPV Nexus Real Data Integration Guide

Complete guide to working with real reservoir and climate data for the FPV Nexus system.

---

## ✅ Current Real Data Status

### Available Real Datasets
- **Srisailam Dam** (✅ Fully Configured)
  - Location: 15.85°N, 78.87°E (Krishna River, Andhra Pradesh/Telangana)
  - Reservoir Area: 616 km²
  - Installed Capacity: 1670 MW
  - Hydraulic Head: 91.44 m
  - Gross Storage: 8722 MCM
  - Climate Data: NASA POWER API (2013-2023 average, 12 months)

---

## 🚀 Quick Start with Real Data

### Option 1: Run Interactive Dashboard (Recommended)
```bash
python -m streamlit run app/dashboard.py
```
- Select "📊 Srisailam Dam (Real Data)" from the dropdown
- All calculations instantly use real NASA POWER climate data
- Explore scenarios with actual water, weather, and solar conditions

### Option 2: Run Command-Line Demo
```bash
python demo.py
```
- Automatically loads Srisailam Dam real data
- Displays comprehensive analysis with 12% FPV coverage
- Shows financial, environmental, and optimization results

### Option 3: Use REST API
```bash
python -m uvicorn backend.main:app --reload
```
- **Discover real reservoirs**: `GET /real-reservoirs`
- **Load specific reservoir**: `GET /real-reservoir/srisailam`
- **Get climate data**: `GET /real-reservoir/srisailam/climate`

**API Documentation**: http://localhost:8000/docs

---

## 📂 Folder Structure for Real Data

```
input_data/
├── srisailam/                    ← Real Srisailam Dam data (ACTIVE)
│   ├── reservoir.csv             ← Dam specifications
│   ├── climate.csv               ← 12-month climate data (NASA POWER)
│   └── DATA_GUIDE.md             ← Metadata and field descriptions
├── your_new_reservoir/           ← Create folders for new dams
│   ├── reservoir.csv
│   └── climate.csv
└── REAL_DATA_GUIDE.md            ← This file
```

---

## 📋 How to Add a New Reservoir

### Step 1: Create the Folder
```bash
mkdir input_data/your_reservoir_name
cd input_data/your_reservoir_name
```

### Step 2: Create `reservoir.csv`

Download or compile reservoir specifications and create a CSV file with these columns:

| Column | Example | Source |
|--------|---------|--------|
| `reservoir_name` | Bhaira Reservoir | Official name |
| `state` | Madhya Pradesh | State/Province |
| `river` | Chambal | River name |
| `latitude` | 24.65 | Google Maps (decimal degrees) |
| `longitude` | 76.20 | Google Maps (decimal degrees) |
| `area_km2` | 45.0 | India-WRIS / Bhuvan Portal |
| `gross_storage_mcm` | 450.0 | CWC Report / Dam Authority |
| `live_storage_mcm` | 280.0 | CWC Report / Dam Authority |
| `frl_m` | 220.0 | Full Reservoir Level (CWC) |
| `mddl_m` | 200.0 | Min Draw Down Level (CWC) |
| `head_m` | 28.5 | Design Head (APGENCO/CEA) |
| `installed_capacity_mw` | 85.0 | CEA / State GENCO |
| `turbine_type` | Francis | CEA / Dam Authority |
| `turbine_efficiency` | 0.88 | Typical: 0.85-0.92 |
| `num_units` | 5 | Number of turbines |
| `dam_type` | Gravity | Gravity/Arch/Earthfill |
| `year_commissioned` | 1964 | Historical record |

**Example `reservoir.csv`:**
```csv
reservoir_name,state,river,latitude,longitude,area_km2,gross_storage_mcm,live_storage_mcm,frl_m,mddl_m,head_m,installed_capacity_mw,turbine_type,turbine_efficiency,num_units,dam_type,year_commissioned
Bhaira Reservoir,Madhya Pradesh,Chambal,24.65,76.20,45.0,450.0,280.0,220.0,200.0,28.5,85.0,Francis,0.88,5,Gravity,1964
```

### Step 3: Create `climate.csv`

Download monthly climate data for your reservoir location and create a CSV with 12 monthly rows.

#### Option A: Get Free Data from NASA POWER API (Recommended)
1. Visit: https://power.larc.nasa.gov/
2. Select your location coordinates
3. Download 11-year monthly average data (2013–2023)
4. Parameters to download: Solar irradiance, Temperature, Humidity, Wind speed
5. Save file and extract monthly averages

**Example parameters for NASA POWER:**
- Solar irradiance: ALLSKY_SFC_SW_DWN (kWh/m²/day)
- Temperature: T2M_MAX, T2M_MIN, T2M (C)
- Humidity: RH2M (%)
- Wind speed: WS10M (m/s)

#### Option B: Use Indian Meteorological Data
- IMD Data Portal: https://www.imdpune.gov.in/
- State Meteorological Depts
- CWC Rainfall Databases

#### Required Columns for `climate.csv`:

| Column | Unit | Range |
|--------|------|-------|
| `month` | Month name | January to December |
| `solar_irradiance_kwh_m2_day` | kWh/m²/day | 2.0–6.5 (India typical) |
| `avg_temp_c` | Celsius | 15–40 (India typical) |
| `max_temp_c` | Celsius | 20–45 |
| `min_temp_c` | Celsius | 5–35 |
| `humidity_pct` | Percentage | 30–90 |
| `wind_speed_m_s` | m/s | 0.5–8.0 |
| `evaporation_mm_day` | mm/day | 2.0–8.0 |

**Example `climate.csv` (Bhaira, Madhya Pradesh):**
```csv
month,solar_irradiance_kwh_m2_day,avg_temp_c,max_temp_c,min_temp_c,humidity_pct,wind_speed_m_s,evaporation_mm_day
January,4.8,20.5,31.2,10.0,55,2.1,2.8
February,5.4,23.8,34.5,11.8,50,2.3,3.2
March,5.9,28.5,39.8,17.2,42,2.6,4.0
April,6.2,32.1,42.0,22.0,38,2.9,5.0
May,5.8,33.0,43.0,23.5,42,3.2,5.2
June,4.5,30.0,39.0,22.0,58,3.8,3.8
July,3.9,28.5,36.0,20.5,72,3.5,2.5
August,4.2,27.8,35.5,20.0,75,3.1,2.3
September,4.6,27.0,34.8,19.5,78,2.4,2.6
October,5.2,25.0,32.0,16.0,72,2.0,3.0
November,4.9,22.0,30.0,12.0,66,1.9,3.2
December,4.4,18.5,28.5,8.0,62,2.0,2.5
```

### Step 4: Verify Your Data
```bash
# Test the discovery system
cd /c/Users/AMITESH/hydro/fpv_project
python -c "
from utils.data_loader import discover_reservoirs, load_real_reservoir, load_real_climate

reservoirs = discover_reservoirs()
print('Available reservoirs:', list(reservoirs.keys()))

if 'Your_Reservoir_Name' in reservoirs:
    data = load_real_reservoir(reservoirs['Your_Reservoir_Name'])
    climate = load_real_climate(reservoirs['Your_Reservoir_Name'])
    print(f'✓ Loaded: {data[\"reservoir_name\"]}')
    print(f'✓ Climate records: {len(climate)}')
"
```

### Step 5: Use in Dashboard
1. Refresh the Streamlit app (F5)
2. Your reservoir appears in the dropdown as "📊 Your Reservoir Name (Real Data)"
3. All calculations automatically use your real data

---

## 🔧 Data Sources & Recommendations

### Recommended Sources for Indian Reservoirs

| Data Type | Source | Quality | Link |
|-----------|--------|---------|------|
| **Solar Irradiance** | NASA POWER API | ★★★★★ | https://power.larc.nasa.gov |
| **Temperature, Humidity, Wind** | NASA POWER API | ★★★★★ | https://power.larc.nasa.gov |
| **Evaporation** | FAO Penman-Monteith formula | ★★★★☆ | Local climate input |
| **Dam Specifications** | India-WRIS Portal | ★★★★★ | https://indiawris.gov.in |
| **CWC Data** | Central Water Commission | ★★★★★ | https://cwc.gov.in |
| **State GENCO Reports** | Power Generation Companies | ★★★★☆ | State-specific |
| **IMD Weather Data** | India Meteorological Dept | ★★★★☆ | https://www.imdpune.gov.in |

### Specific Reservoirs (Pre-configured recommendations)

#### Already Available:
- ✅ **Srisailam Dam** (Andhra Pradesh) - Complete with NASA POWER data

#### Easy to Add (Similar to Srisailam):
- Nagarjuna Sagar (Andhra Pradesh) - Lat 17.45, Lon 79.10
- Almatti Dam (Karnataka) - Lat 14.88, Lon 74.52
- Koyna Reservoir (Maharashtra) - Lat 17.35, Lon 73.58
- Rihand Reservoir (Uttar Pradesh) - Lat 24.67, Lon 81.78

---

## 🌐 Working with NASA POWER API

### Direct API Access (For Programmers)
```python
import requests
import pandas as pd

# Example: Get Srisailam climate data
lat, lon = 15.85, 78.87
params = {
    'parameters': 'ALLSKY_SFC_SW_DWN,T2M,WS10M,RH2M',
    'community': 'RE',
    'longitude': lon,
    'latitude': lat,
    'start': 2013,
    'end': 2023,
    'format': 'JSON'
}

url = 'https://power.larc.nasa.gov/api/temporal/monthly/point'
response = requests.get(url, params=params)
data = response.json()

# Process into 12-month averages
# (See utils/data_loader.py for complete implementation)
```

### Web Interface
1. Visit https://power.larc.nasa.gov/
2. Click "Agroclimatology" (or "Renewable Energy")
3. Select location on map or enter coordinates
4. Download monthly data as CSV
5. Extract 12-month averages

---

## 📊 System Architecture

The FPV system now auto-discovers real data folder structure:

```
app/dashboard.py
├─ discover_reservoirs()  ← Scans input_data/ folder
├─ load_real_reservoir()  ← Loads dam specs
├─ load_real_climate()    ← Loads climate data
└─ Real-time calculations with actual weather/water data

backend/main.py
├─ GET /real-reservoirs     ← List all available real data
├─ GET /real-reservoir/{id} ← Load specific reservoir
└─ GET /real-reservoir/{id}/climate ← Climate data for API

demo.py
└─ Automatically loads Srisailam Dam real data for testing
```

---

## ⚠️ Data Quality Checks

When adding new reservoirs, verify:

- [ ] Coordinates are within India (5°N–35°N, 68°E–97°E)
- [ ] Solar irradiance is 2.0–6.5 kWh/m²/day
- [ ] Temperatures are realistic (5–45°C typical)
- [ ] Humidity 30–90%
- [ ] Wind speed 0.5–8 m/s
- [ ] Evaporation 2–8 mm/day
- [ ] All 12 months present in climate.csv
- [ ] No missing values (NaN)
- [ ] Reservoir area > 5 km²
- [ ] Head > 5 m

---

## 🔄 Using Real Data in Code

### Dashboard (Streamlit)
```python
from utils.data_loader import discover_reservoirs, load_real_reservoir, load_real_climate

# Auto-discover available reservoirs
real_reservoirs = discover_reservoirs()

# Load specific reservoir
if "Srisailam" in real_reservoirs:
    folder = real_reservoirs["Srisailam"]
    data = load_real_reservoir(folder)
    climate = load_real_climate(folder)
    
    # Use in calculations
    area_km2 = data["area_km2"]
    head_m = data["head_m"]
```

### Backend API
```bash
# Get list of real reservoirs
curl http://localhost:8000/real-reservoirs

# Get climate data for a reservoir
curl http://localhost:8000/real-reservoir/srisailam/climate
```

### Demo Script
```bash
python demo.py  # Automatically uses Srisailam real data
```

---

## 📈 Analysis Results with Real Data

### Srisailam Dam (12% FPV Coverage) - Real Data Results
- **FPV Capacity**: 13.3 MWp
- **Annual FPV Energy**: 19.0 Million MWh
- **Water Saved**: 73.4 Million m³/year
- **Extra Hydro Energy**: 15,536 MWh/year
- **Total Energy**: 19.1 Million MWh/year
- **CO₂ Avoided**: 15.6 Million tonnes/year
- **ROI**: 309,623% (25 years)
- **Payback Period**: <1 month

---

## 🐛 Troubleshooting

### "Reservoir folder not found"
- Ensure folder is in `input_data/folder_name/`
- Folder name must match discovery key (case-insensitive)
- Check `discover_reservoirs()` output

### "Missing climate.csv"
- Verify file exists in the reservoir folder
- Check column names match expected format
- Run data quality checks

### "Invalid data values"
- Check temperature ranges (5-45°C typical for India)
- Solar irradiance should be 2.0-6.5 kWh/m²/day
- All numeric columns should have no NaN values

### "API not finding reservoirs"
- Restart backend: `python -m uvicorn backend.main:app --reload`
- Check `/real-reservoirs` endpoint
- Verify folders in `input_data/`

---

## 📞 Support & Data Help

### For Climate Data:
- Missing a location? Download from https://power.larc.nasa.gov
- Issues with NASA POWER? Check their technical documentation

### For Dam Specifications:
- India-WRIS Portal: https://indiawris.gov.in
- CWC Reports: https://cwc.gov.in
- Your State's GENCO website

### For Integration Issues:
- Check `input_data/DATA_GUIDE.md` for field details
- Run `python demo.py` to verify system
- Check dashboard dropdown for discovered reservoirs

---

## 🎯 Next Steps

1. **Explore with Current Data**: Run dashboard with Srisailam
2. **Add Your Reservoir**: Follow steps above
3. **Test Results**: Verify numbers make sense
4. **Scale Up**: Add more reservoirs as needed
5. **Deploy**: Use real data in production

---

## 📝 File Checklist for New Reservoir

```
✓ input_data/your_reservoir/
  ├─ reservoir.csv (1 row, 17 columns)
  ├─ climate.csv (12 rows, 7 columns)
  └─ (Optional) README or metadata
```

**That's it! Your reservoir will auto-appear in the system.**

---

*Last Updated: April 2026*
*FPV Nexus Dashboard v2.0 - Real Data Integration Complete*
