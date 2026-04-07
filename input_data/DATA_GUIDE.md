# 📂 Input Data Guide — FPV Nexus

This folder is where you place **real reservoir and climate data** for analysis.

---

## 📁 Folder Structure

```
input_data/
├── srisailam/              ← Pre-loaded with real data ✅
│   ├── reservoir.csv       ← Dam specifications
│   └── climate.csv         ← 12-month climate data (NASA POWER)
├── your_reservoir/         ← Create a folder for each new reservoir
│   ├── reservoir.csv
│   └── climate.csv
└── DATA_GUIDE.md           ← This file
```

---

## 📊 What Data You Need

### 1. `reservoir.csv` — Dam Specifications

| Column | Description | Where to Get |
|--------|-------------|-------------|
| `reservoir_name` | Name of the dam | — |
| `state` | Indian state | — |
| `river` | River name | — |
| `latitude` | Latitude (decimal degrees) | Google Maps |
| `longitude` | Longitude (decimal degrees) | Google Maps |
| `area_km2` | Reservoir surface area at FRL (km²) | India-WRIS / Bhuvan |
| `gross_storage_mcm` | Gross storage capacity (MCM) | India-WRIS / CWC |
| `live_storage_mcm` | Live storage (MCM) | India-WRIS / CWC |
| `frl_m` | Full Reservoir Level (m MSL) | CWC / Dam authority |
| `mddl_m` | Min Draw Down Level (m MSL) | CWC / Dam authority |
| `head_m` | Design hydraulic head (m) | APGENCO / CEA |
| `installed_capacity_mw` | Total hydro capacity (MW) | CEA / State GENCO |
| `turbine_type` | Francis / Kaplan / Pelton | CEA |
| `turbine_efficiency` | 0.85–0.92 typically | CEA |
| `num_units` | Number of generating units | CEA |
| `dam_type` | Gravity / Arch / Earthfill | — |
| `year_commissioned` | Year of commissioning | — |

### 2. `climate.csv` — 12-Month Climate Data

| Column | Unit | Where to Get |
|--------|------|-------------|
| `month` | Month name | — |
| `solar_irradiance_kwh_m2_day` | kWh/m²/day | **NASA POWER** ✅ |
| `avg_temp_c` | °C | **NASA POWER** ✅ |
| `max_temp_c` | °C | **NASA POWER** ✅ |
| `min_temp_c` | °C | **NASA POWER** ✅ |
| `humidity_pct` | % | **NASA POWER** ✅ |
| `wind_speed_m_s` | m/s | **NASA POWER** ✅ |
| `evaporation_mm_day` | mm/day | IMD / Calculated |

---

## 🌐 Where to Get Data (Free Sources)

### Climate Data — NASA POWER (Recommended ✅)

**URL:** https://power.larc.nasa.gov/data-access-viewer/

**Steps:**
1. Go to the website
2. Select **"Renewable Energy"** community
3. Select **"Monthly"** temporal
4. Enter your dam's **latitude & longitude**
5. Choose parameters:
   - `ALLSKY_SFC_SW_DWN` → Solar Irradiance
   - `T2M` → Average Temperature
   - `T2M_MAX` → Max Temperature
   - `T2M_MIN` → Min Temperature
   - `RH2M` → Relative Humidity
   - `WS10M` → Wind Speed at 10m
6. Set date range (e.g., 2013–2023)
7. Download as **CSV** or **JSON**
8. Average each month across all years

**API (Direct Download):**
```
https://power.larc.nasa.gov/api/temporal/monthly/point?parameters=ALLSKY_SFC_SW_DWN,T2M,T2M_MAX,T2M_MIN,WS10M,RH2M&community=RE&longitude=YOUR_LON&latitude=YOUR_LAT&start=2013&end=2023&format=JSON
```

### Reservoir Data — India-WRIS

**URL:** https://indiawris.gov.in/wris/

**Steps:**
1. Search for your dam
2. Get: Area, Storage, FRL, MDDL

### Hydropower Data — CEA India

**URL:** https://cea.nic.in/

Look for "Installed Capacity" reports → find your dam's MW capacity, head, turbine type.

### State GENCO Websites

| State | GENCO | URL |
|-------|-------|-----|
| Andhra Pradesh | APGENCO | https://apgenco.gov.in |
| Telangana | TSGENCO | https://tsgenco.telangana.gov.in |
| Maharashtra | MAHAGENCO | https://mahagenco.in |
| Karnataka | KPCL | https://kpcl.kar.nic.in |

### Evaporation Data

- **IMD Pune** — publishes pan evaporation data
- **India-WRIS** — some reservoirs have evaporation data
- **Estimate:** Use the Penman formula (our regression model does this!):
  ```
  E ≈ a₀ + a₁·Rs + a₂·T − a₃·RH + a₄·Wind
  ```

---

## ✅ Pre-loaded: Srisailam Dam

The `srisailam/` folder contains **real data**:

| Parameter | Source | Value |
|-----------|--------|-------|
| Area | India-WRIS | 616 km² |
| Head | APGENCO | 91.44 m |
| Capacity | CEA | 1670 MW |
| Climate | NASA POWER (2013–2023 avg) | 12-month data |

---

## 🆕 Adding Your Own Reservoir

1. Create a new folder: `input_data/your_dam_name/`
2. Copy `reservoir.csv` and `climate.csv` from `srisailam/` as templates
3. Replace values with your dam's data
4. Run the dashboard — your dam will appear in the dropdown!
