# 📊 Data Sources Explanation

## Current Srisailam Dam Data

### Where Did It Come From?

**1. Climate Data** (Solar, Temp, Humidity, Wind)
- **Source**: NASA POWER API (free, public)
- **Method**: I queried coordinates 15.85°N, 78.87°E 
- **Period**: 2013-2023 monthly averages
- **URL**: https://power.larc.nasa.gov/api/temporal/monthly/point
- **Fields**: ALLSKY_SFC_SW_DWN, T2M, T2M_MAX, T2M_MIN, RH2M, WS10M

**2. Dam Specifications** (Area, Head, Capacity)
- **Source**: APGENCO official records + India-WRIS
- **Created**: Manually compiled from public sources
- **Verified**: Cross-checked with CWC reports

**3. Evaporation Rate**
- **Method**: Calculated from NASA POWER data using regression model
- **Formula**: FAO Penman-Monteith based on temp, humidity, wind, solar radiation
- **NOT needed separately** - derives from climate data

**4. Water Head Data**
- **Source**: Design head from dam specs (engineering records)
- **Value**: 91.44m (Srisailam design head)
- **Used for**: Hydropower calculation (when water is saved by FPV shading)
- **IS needed** - essential for hydro revenue calculation

---

## Current Data Structure

```
reservoir.csv = Dam specifications (fixed, 1 row)
climate.csv    = 12-month climate data (from NASA POWER API)
```

Both needed! But climate data can be **automatically fetched** from NASA POWER.

---

## 🚀 Plan: 30-50 Major Indian Dams

### Data Sources Available
- **NASA POWER API**: Free, covers entire India, monthly data
- **India-WRIS Portal**: Dam specs (area, storage, head)
- **CWC Reports**: Official dam capacity data
- **APGENCO/State GENCOs**: Power generation specifications

### Workflow
1. **Compile dam list** (30-50 major ones)
2. **Auto-fetch NASA POWER** for each location
3. **Auto-fetch dam specs** from India-WRIS API or CSV
4. **Generate folder structure** automatically
5. **Create interactive map** showing all dams
6. **Dashboard**: Click dam → See analysis

---

## Data Matrix: What You Need for Each Dam

| Field | Required? | Source | Auto? |
|-------|-----------|--------|-------|
| Lat/Lon | ✅ YES | Google Maps | Manual |
| Dam Name | ✅ YES | Wikipedia/CWC | Manual |
| Reservoir Area (km²) | ✅ YES | India-WRIS | ⚙️ Auto |
| Head (m) | ✅ YES | India-WRIS | ⚙️ Auto |
| Installed Capacity (MW) | ✅ YES | CWC | ⚙️ Auto |
| **Solar Irradiance** | ✅ YES | NASA POWER | **🤖 AUTO** |
| **Temperature** | ✅ YES | NASA POWER | **🤖 AUTO** |
| **Humidity** | ✅ YES | NASA POWER | **🤖 AUTO** |
| **Wind Speed** | ✅ YES | NASA POWER | **🤖 AUTO** |
| **Evaporation** | Auto-calculated | From climate | **🤖 AUTO** |
| Year Commissioned | ❌ NO | Optional | Manual |
| Storage Type | ❌ NO | Optional | Manual |

**Green 🤖 = Automatically fetched from NASA POWER API**

---

## Next: 50-Dam Database Coming

Soon I'll create:
- ✅ List of 50 major Indian dams with coordinates
- ✅ Automatic NASA POWER data fetching
- ✅ Auto-generation of all CSV folders
- ✅ Interactive India map with dots
- ✅ Click → Load dam → Show analysis
