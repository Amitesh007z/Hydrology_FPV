# 🚀 FPV NEXUS — Enhanced Product Requirements Document (PRD)

**Version:** 2.0 — Research-Integrated Edition  
**Date:** April 7, 2026  
**Status:** Living Document  

---

## 1. 🌍 Product Vision

### From Dashboard → Decision Intelligence Platform

> **FPV Nexus** is an intelligent energy co-optimization platform that helps governments, utilities, and energy companies **maximize energy output, water savings, and ROI from hydropower reservoirs** through floating solar integration.

**Core Hook:**  
> Covering just **~3% of a reservoir's surface can effectively double its energy capacity.**

---

## 2. 🎯 Problem Statement

Derived from primary research and published literature:

| Problem | Evidence |
|---|---|
| Hydropower share declining, thermal increasing | CO₂ emissions ↑ nationally |
| Land scarcity limits ground-mounted solar expansion | Urban + agricultural competition |
| Reservoir evaporation losses are massive | e.g., **917 MCM/year** for large Indian reservoirs |
| Solar & hydro operate independently | No joint optimization exists in production tools |

### 💡 Core Gap

> **No system exists that jointly optimizes solar + hydro + water + economics in real-time.**

---

## 3. 🧠 Core Product Modules

### 3.1 — Solar Generation Engine

#### A. Installed Capacity (STC)

```
P_dc (MWp) = Area (m²) × Coverage × Efficiency / 10⁶
```

> At Standard Test Conditions (STC): Irradiance = 1000 W/m², Cell Temp = 25°C.

#### B. Cell Temperature — Fuentes / NOCT Model

```
T_cell = T_air + (G / 1000) × (NOCT − 20) / 80
```

| Symbol | Meaning | Typical Value |
|--------|---------|---------------|
| `T_air` | Ambient air temperature | 25–35 °C |
| `G` | Irradiance on panel surface | 800–1100 W/m² |
| `NOCT` | Nominal Operating Cell Temperature | 45 °C |

> **FPV Advantage:** Water cooling reduces `T_cell` by 5–10°C vs. ground-mount, improving yield by ~2–5%.

#### C. Temperature Coefficient Loss

```
L_temp = 1 + γ × (T_cell − 25)
```

| Symbol | Meaning | Value |
|--------|---------|-------|
| `γ` | Temp coefficient of power | −0.004 /°C (Si panels) |

> Clamped to a minimum of 0.70 to prevent unrealistic results.

#### D. Daily Energy Yield

```
E_fpv (MWh/day) = Area (m²) × Coverage × Irradiance (kWh/m²/day) × η × PR × L_temp / 1000
```

| Parameter | Range | Default |
|-----------|-------|---------|
| Coverage | 1–50% | 10% |
| η (Efficiency) | 15–22% | 18% |
| PR (Performance Ratio) | 0.60–0.85 | 0.75 |

#### E. Annual Energy

```
E_annual (MWh) = E_fpv (MWh/day) × 365
```

---

### 3.2 — Water Intelligence Engine

#### A. Simple Shading Model (Currently Implemented)

```
V_saved (m³) = Area_covered (m²) × (Evap_mm/day × 365 / 1000) × Shading_Factor
```

| Parameter | Meaning | Default |
|-----------|---------|---------|
| Shading Factor | % of evaporation prevented by panel cover | 0.70 (70%) |
| Variation | Climate multiplier (dry year, wet year) | 1.0 |

#### B. Regression-Based Evaporation Model (📄 From Paper — Enhancement)

Research literature provides a more accurate, multi-variable regression model:

```
E = a₀ + a₁·Rₛ + a₂·Tₐ − a₃·RH + a₄·u₁₀
```

| Symbol | Meaning |
|--------|---------|
| `Rₛ` | Incoming solar radiation (MJ/m²/day) |
| `Tₐ` | Air temperature (°C) |
| `RH` | Relative humidity (%) |
| `u₁₀` | Wind speed at 10m height (m/s) |
| `a₀…a₄` | Regression coefficients (site-specific) |

> **PRD Enhancement:** Support **both** the simple shading model and this regression model. Add a toggle in the UI for "Simple" vs. "Advanced" evaporation estimation.

#### C. Seasonal Variation Factors

| Season | Multiplier | Reasoning |
|--------|------------|-----------|
| Summer (Mar–May) | ×1.4 | High temp, low humidity |
| Monsoon (Jun–Sep) | ×0.6 | Cloud cover, high humidity |
| Winter (Oct–Feb) | ×0.8 | Lower solar input |

#### D. Structure-Based Modeling (📄 From Paper — Enhancement)

Evaporation reduction varies by FPV structure type:

| Structure | Shading Factor | Notes |
|-----------|---------------|-------|
| **Pontoon-based** | 0.70–0.80 | Rigid, higher coverage density |
| **Flexible float** | 0.50–0.65 | Lighter, lower shading |

> **PRD Enhancement:** Add a "Structure Type" selector in the UI.

---

### 3.3 — Hydro Conversion Engine

#### A. Extra Energy from Saved Water

Based on gravitational potential energy:

```
E_hydro (MWh) = V × ρ × g × h × η_turbine / 3.6 × 10⁹
```

| Symbol | Meaning | Value |
|--------|---------|-------|
| `V` | Volume of saved water (m³) | Computed |
| `ρ` | Water density | 1000 kg/m³ |
| `g` | Gravitational acceleration | 9.81 m/s² |
| `h` | Effective hydraulic head (m) | Site-specific |
| `η_turbine` | Turbine-generator efficiency | 0.85 |

#### B. Instantaneous Power (📄 From Paper)

```
P (MW) = η × ρ × g × Q × h / 10⁶
```

> Where `Q` = flow rate (m³/s). Useful for **time-of-day dispatch modeling**.

#### C. Capacity Factor

```
CF = Annual_Energy (MWh) / (Installed_Capacity (MW) × 8760)
```

#### D. Revenue

```
Revenue (₹ Crores) = E_hydro (MWh) × Tariff (₹/kWh) × 1000 / 10⁷
```

---

### 3.4 — Environmental Engine

#### A. CO₂ Avoided

```
CO₂ (tonnes) = (E_fpv + E_hydro) × Grid_Emission_Factor
```

| Parameter | Value | Source |
|-----------|-------|--------|
| India Grid EF | 0.82 kg CO₂/kWh | CEA 2023 |

#### B. Environmental Equivalents

| Metric | Formula | Typical Factor |
|--------|---------|----------------|
| 🌳 Trees Planted | CO₂ / 0.025 | tonnes/tree/year |
| 🚗 Cars Removed | CO₂ / 2.31 | tonnes/car/year |
| 🛢️ Oil Saved (liters) | CO₂ × 1000 / 2.35 | kg CO₂/liter |

#### C. SDG Alignment

| SDG | Contribution |
|-----|-------------|
| SDG 6 — Clean Water | Water savings quantified |
| SDG 7 — Affordable Energy | Renewable generation |
| SDG 13 — Climate Action | CO₂ reduction |
| SDG 12 — Responsible Consumption | Resource efficiency |

---

### 3.5 — Financial Engine (🆕 From Paper)

> [!IMPORTANT]
> This module is the **key product differentiator**. It transforms a technical dashboard into a **bankable feasibility tool**.

#### A. Levelized Cost of Energy (LCOE)

```
LCOE = Σ [(I_t + M_t + F_t) / (1+r)^t] / Σ [E_t / (1+r)^t]
```

| Symbol | Meaning |
|--------|---------|
| `I_t` | Investment expenditure in year `t` |
| `M_t` | O&M cost in year `t` |
| `F_t` | Fuel cost (0 for solar) |
| `E_t` | Energy generated in year `t` |
| `r` | Discount rate (8–12% typical) |

#### B. Return on Investment

```
ROI = Net_Profit / Total_Investment × 100%
```

#### C. Payback Period

```
Payback (years) = CAPEX / Annual_Net_Revenue
```

> From paper: typical FPV payback is **~5 years** for Indian reservoirs.

---

## 4. 🔄 System Flow (Enhanced — 6 Layers)

```
┌──────────────────────────────────────────────────────────┐
│  LAYER 1: DATA INGESTION                                 │
│  Reservoir DB · Climate APIs · Satellite · Hydro History │
└──────────────────────┬───────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│  LAYER 2: SIMULATION ENGINE                              │
│  Coverage scenarios (1%, 5%, 10%, ECOH)                  │
│  Structure type (Pontoon / Float)                        │
│  Seasonal simulation (12-month curves)                   │
└──────────────────────┬───────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│  LAYER 3: OPTIMIZATION (🆕)                              │
│  Maximize: Energy + WaterSavings + ROI                   │
│  Subject to:                                             │
│    • Coverage ≤ 10% (ecological constraint)              │
│    • Grid capacity limit                                 │
│    • Budget / CAPEX cap                                  │
│  Solver: OR-Tools / Pyomo                                │
└──────────────────────┬───────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│  LAYER 4: DECISION INTELLIGENCE                          │
│  Optimal coverage % · Best structure · Expected ROI      │
│  Payback period · Risk assessment                        │
└──────────────────────┬───────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│  LAYER 5: VISUALIZATION                                  │
│  KPI Cards · Scenario Comparison · Monthly Curves        │
│  Trade-off Graphs · Sensitivity Analysis                 │
└──────────────────────┬───────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│  LAYER 6: ACTION (🆕)                                    │
│  Export PDF Reports · API for Govt Planning               │
│  Investment Recommendation · Carbon Credit Estimation    │
└──────────────────────────────────────────────────────────┘
```

---

## 5. 🧩 Key Features

| # | Feature | Status | Description |
|---|---------|--------|-------------|
| 1 | **Scenario Simulator** | ✅ Built | Coverage sliders, reservoir presets, climate inputs |
| 2 | **Smart Optimizer** | 🆕 Planned | "Best ROI" / "Max Energy" / "Water Priority" modes |
| 3 | **Hybrid Energy Planner** | 🆕 Planned | Solar + hydro joint scheduling, time-of-day dispatch |
| 4 | **Climate-Aware Predictions** | ✅ Partial | Seasonal variation; future: ML-based forecasting |
| 5 | **Financial Dashboard** | 🆕 Planned | LCOE, ROI, payback period, carbon credit valuation |
| 6 | **Feasibility Report Export** | ✅ Built | Text export; future: PDF with charts |
| 7 | **Structure Type Selector** | 🆕 Planned | Pontoon vs. Float comparison |

---

## 6. 📊 Differentiation — Product vs. Research Paper

| Dimension | FPV Nexus (Product) | Research Paper |
|-----------|-------------------|----------------|
| Static analysis | ❌ | ✅ |
| Real-time simulation | ✅ | ❌ |
| Optimization engine | ✅ (planned) | ❌ |
| Financial modeling (LCOE, ROI) | ✅ (planned) | ⚠️ Limited |
| Interactive UI | ✅ | ❌ |
| Multi-reservoir support | ✅ | Single case |
| SaaS / API ready | ✅ | ❌ |
| Actionable recommendations | ✅ | Descriptive only |

---

## 7. 💰 Monetization Strategy

| Segment | Model | Target |
|---------|-------|--------|
| **B2G** (Government) | Per-reservoir feasibility license | MNRE, State Utilities, NHPC |
| **B2B** (Industry) | Enterprise subscription | NTPC, SECI, Solar EPC firms |
| **SaaS** | Tiered pricing | Independent analysts, researchers |
| **Carbon Credits** | Revenue share on validated credits | International markets |

---

## 8. 🏗️ Architecture

```
┌─────────────────────┐     ┌─────────────────────┐
│  FRONTEND (React)   │────▶│  BACKEND (FastAPI)   │
│  Recharts · Lucide  │◀────│  Pydantic · CORS     │
└─────────────────────┘     └──────────┬────────────┘
                                       │
                            ┌──────────▼────────────┐
                            │  COMPUTATION ENGINE    │
                            │  models/fpv.py         │
                            │  models/evaporation.py │
                            │  models/hydro.py       │
                            │  models/co2.py         │
                            └──────────┬────────────┘
                                       │
                            ┌──────────▼────────────┐
                            │  🆕 OPTIMIZATION SVC   │
                            │  OR-Tools / Pyomo      │
                            │  Constraint Solver     │
                            └───────────────────────┘
```

**Deployment:** Docker Compose → Render / GCP Cloud Run / AWS

---

## 9. 📈 Roadmap

### Phase 1 — Foundation ✅ Done
- Physics-based computation models (FPV, Hydro, Evaporation, CO₂)
- Streamlit interactive dashboard
- React + FastAPI production stack
- Docker deployment
- 5 Indian reservoir datasets

### Phase 2 — Product Upgrade (Next)
- [ ] Financial modeling UI (LCOE, ROI, Payback)
- [ ] Optimization engine (OR-Tools / Pyomo)
- [ ] Multi-scenario comparison view
- [ ] Structure type selector (Pontoon vs. Float)
- [ ] Advanced evaporation model (regression-based)

### Phase 3 — Intelligence Layer 🚀
- [ ] ML-based energy prediction (weather → output)
- [ ] Reservoir recommendation engine
- [ ] PDF feasibility report export
- [ ] Carbon credit estimation module

### Phase 4 — Platform Vision
- [ ] "Google Maps for Energy Planning" — click any reservoir → full analysis
- [ ] Satellite-based reservoir detection
- [ ] Multi-country expansion
- [ ] Mobile app (React Native)

---

## 10. 📚 Scientific References

1. Rosa-Clot et al. — "Floating PV Systems" (IEEE 2020)
2. Trapodi et al. — "Environmental Impact of FPV" (Renewable Energy 2021)
3. Adeh et al. — "Solar Panels Reduce Evaporation from Reservoirs" (Nature 2022)
4. CEA India — Grid emission factors, hydropower standards
5. MNRE Guidelines — Solar power project norms

---

## 11. ⭐ Summary

| What Exists | What This PRD Adds |
|---|---|
| Strong physics engine | Optimization layer + Financial engine |
| Full-stack deployed system | Product strategy + Monetization |
| Real Indian datasets | Advanced models from research papers |
| Interactive dashboard | Decision intelligence + Action layer |
| A project | **A scalable climate-tech product** |

---

> **FPV Nexus v2.0** — From Dashboard to Decision Intelligence Platform  
> **☀️💧⚡🌍**
