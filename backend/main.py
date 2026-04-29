"""
FastAPI Backend for FPV Nexus Dashboard v2.0
Exposes computation models as REST APIs
Includes: Financial Engine, Optimizer, Structure Type, Advanced Evaporation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import sys
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import (
    compute_fpv_power, compute_annual_fpv_energy, compute_fpv_capacity,
    compute_cell_temperature, compute_temp_coefficient_loss,
    compute_evaporation_reduction_volume,
    compute_regression_evaporation, compute_structure_shading_factor,
    compute_extra_hydro_energy, compute_revenue_from_hydro,
    compute_total_co2_avoided, compute_equivalent_trees, compute_equivalent_cars,
    compute_full_financial_analysis, FINANCIAL_DEFAULTS,
    optimize_scenario, compare_scenarios
)
from models.generation_data import get_current_generation
from utils import (
    load_reservoir_data, get_monthly_climate_data, compute_annual_averages,
    discover_reservoirs, load_real_reservoir, load_real_climate
)
from thermal_data import get_thermal_grid_data, get_thermal_legend

# Initialize FastAPI app
app = FastAPI(
    title="FPV Nexus API",
    description="Floating Solar-Hydro Co-Optimization Backend v2.0 — Decision Intelligence Platform",
    version="2.0.0"
)

# Production-ready CORS configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3003",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3003",
]

# Add production frontend URLs from environment
if os.getenv("FRONTEND_URL"):
    ALLOWED_ORIGINS.append(os.getenv("FRONTEND_URL"))

# Allow all vercel deployments in development, restrict in production
if os.getenv("ENV", "development") == "development":
    ALLOWED_ORIGINS.append("https://vercel.app")  # All Vercel apps
    ALLOWED_ORIGINS.append("*")  # Allow all
else:
    # Production: only allow specific domains
    if os.getenv("PRODUCTION_FRONTEND_URL"):
        ALLOWED_ORIGINS.append(os.getenv("PRODUCTION_FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# DATA MODELS (Pydantic)
# ============================================================================

class ScenarioInput(BaseModel):
    """Input parameters for FPV scenario calculation"""
    reservoir_name: str = "Custom"
    area_km2: float
    coverage: float  # 0-1
    efficiency: float  # 0.1-0.25
    pr: float = 0.75
    head_m: float
    installed_capacity_mw: float
    avg_irradiance: float
    avg_evaporation: float
    avg_temp: float
    wind_speed: float
    humidity: float = 65.0
    temp_variation: float = 1.0
    emission_factor: float = 0.82
    hydro_tariff: float = 4.5
    # NEW v2.0 fields
    structure_type: str = "pontoon"
    evap_model: str = "simple"  # "simple" or "regression"
    capex_cr_per_mwp: float = 4.0
    fpv_tariff: float = 3.5
    discount_rate: float = 0.10
    project_lifetime: int = 25


class ScenarioOutput(BaseModel):
    """Output results from scenario calculation"""
    # FPV Results
    fpv_capacity_mwp: float
    daily_fpv_mwh: float
    annual_fpv_mwh: float
    cell_temp_c: float
    temp_correction_factor: float

    # Water Results
    water_saved_million_m3: float
    water_saved_liters: float
    shading_factor: float
    evaporation_used: float

    # Hydro Results
    extra_hydro_mwh_annual: float
    capacity_factor_boost: float

    # Energy Mix
    total_energy_mwh: float

    # Environmental Results
    co2_avoided_tonnes: float
    co2_fpv_tonnes: float
    co2_hydro_tonnes: float
    trees_equivalent: float
    cars_offset: float

    # Financial Results (NEW v2.0)
    capex_total_cr: float
    opex_annual_cr: float
    lcoe_inr_per_kwh: float
    lcoe_inr_per_mwh: float
    payback_years: float
    roi_percent: float
    net_profit_cr: float
    fpv_revenue_cr: float
    hydro_revenue_cr: float
    carbon_credit_cr: float
    total_annual_revenue_cr: float

    # Summary
    summary: Dict


class OptimizeInput(BaseModel):
    """Input for optimization endpoint"""
    area_km2: float
    head_m: float
    irradiance: float
    evaporation: float
    mode: str = "max_energy"
    max_coverage: float = 0.10
    efficiency: float = 0.18
    pr: float = 0.75
    shading_factor: float = 0.70
    capex_cr_per_mwp: float = 4.0
    fpv_tariff: float = 3.5
    hydro_tariff: float = 4.5
    emission_factor: float = 0.82


class ReservoirData(BaseModel):
    """Reservoir information"""
    name: str
    area_km2: float
    head_m: float
    installed_capacity_mw: float
    storage_capacity_mcm: float


class ClimateData(BaseModel):
    """Monthly climate data"""
    month: str
    avg_temp: float
    solar_irradiance: float
    evaporation: float


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", tags=["Health"])
def read_root():
    """Health check endpoint"""
    return {
        "status": "✅ FPV Nexus API Running",
        "version": "2.0.0",
        "endpoints": "/docs",
        "new_features": ["financial_engine", "optimizer", "structure_types", "regression_evaporation"]
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "api": "FPV Nexus",
        "version": "2.0.0",
        "modules": ["fpv", "hydro", "evaporation", "co2", "financial", "optimizer"]
    }


@app.get("/reservoirs", response_model=List[ReservoirData], tags=["Data"])
def get_reservoirs():
    """Get list of preset reservoirs"""
    reservoirs_list = [
        ReservoirData(name="Bhaira Reservoir", area_km2=45.0, head_m=28.5, installed_capacity_mw=85.0, storage_capacity_mcm=450.0),
        ReservoirData(name="Rana Pratap Sagar", area_km2=89.5, head_m=32.0, installed_capacity_mw=115.0, storage_capacity_mcm=1156.0),
        ReservoirData(name="Indira Sagar", area_km2=245.0, head_m=58.0, installed_capacity_mw=1000.0, storage_capacity_mcm=1450.0),
        ReservoirData(name="Koyna Reservoir", area_km2=56.8, head_m=48.0, installed_capacity_mw=1960.0, storage_capacity_mcm=1259.0),
        ReservoirData(name="Krishnarajsagar", area_km2=27.5, head_m=12.0, installed_capacity_mw=44.0, storage_capacity_mcm=256.0),
    ]
    return reservoirs_list


@app.get("/real-reservoirs", tags=["Data"])
def get_real_reservoirs():
    """Discover and list all real reservoirs with actual data"""
    real_reservoirs = discover_reservoirs()
    result = []
    
    for name, folder_path in real_reservoirs.items():
        try:
            data = load_real_reservoir(folder_path)
            result.append({
                "name": data["reservoir_name"],
                "display_name": name,
                "state": data.get("state", ""),
                "river": data.get("river", ""),
                "latitude": data.get("latitude", 0),
                "longitude": data.get("longitude", 0),
                "area_km2": data["area_km2"],
                "head_m": data["head_m"],
                "installed_capacity_mw": data["installed_capacity_mw"],
                "gross_storage_mcm": data.get("gross_storage_mcm", 0),
                "live_storage_mcm": data.get("live_storage_mcm", 0),
                "data_source": "Real Data (NASA POWER + Official Records)"
            })
        except Exception as e:
            pass
    
    return {"count": len(result), "reservoirs": result}


@app.get("/real-reservoir/{reservoir_id}", tags=["Data"])
def get_real_reservoir(reservoir_id: str):
    """Load specific real reservoir with full details"""
    real_reservoirs = discover_reservoirs()
    
    for name, folder_path in real_reservoirs.items():
        if name.lower().replace(" ", "_") == reservoir_id.lower().replace(" ", "_"):
            try:
                data = load_real_reservoir(folder_path)
                climate = load_real_climate(folder_path)
                
                return {
                    "success": True,
                    "reservoir": data,
                    "climate_months": len(climate),
                    "climate_summary": {
                        "avg_solar_irradiance": float(climate["solar_irradiance"].mean()) if "solar_irradiance" in climate.columns else 0,
                        "avg_temp": float(climate["avg_temp"].mean()) if "avg_temp" in climate.columns else 0,
                        "avg_evaporation": float(climate["evaporation"].mean()) if "evaporation" in climate.columns else 0,
                        "avg_humidity": float(climate["humidity"].mean()) if "humidity" in climate.columns else 0,
                        "avg_wind_speed": float(climate["wind_speed"].mean()) if "wind_speed" in climate.columns else 0,
                    }
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error loading reservoir: {str(e)}")
    
    raise HTTPException(status_code=404, detail=f"Reservoir '{reservoir_id}' not found")


@app.get("/real-reservoir/{reservoir_id}/climate", tags=["Data"])
def get_real_reservoir_climate(reservoir_id: str):
    """Get monthly climate data for a real reservoir"""
    real_reservoirs = discover_reservoirs()
    
    for name, folder_path in real_reservoirs.items():
        if name.lower().replace(" ", "_") == reservoir_id.lower().replace(" ", "_"):
            try:
                climate = load_real_climate(folder_path)
                climate_list = []
                for _, row in climate.iterrows():
                    climate_list.append({
                        "month": str(row.get("month", "Unknown")),
                        "solar_irradiance": float(row.get("solar_irradiance", 0)) if "solar_irradiance" in climate.columns else 0,
                        "avg_temp": float(row.get("avg_temp", 0)) if "avg_temp" in climate.columns else 0,
                        "max_temp": float(row.get("max_temp", 0)) if "max_temp" in climate.columns else 0,
                        "min_temp": float(row.get("min_temp", 0)) if "min_temp" in climate.columns else 0,
                        "evaporation": float(row.get("evaporation", 0)) if "evaporation" in climate.columns else 0,
                        "humidity": float(row.get("humidity", 0)) if "humidity" in climate.columns else 0,
                        "wind_speed": float(row.get("wind_speed", 0)) if "wind_speed" in climate.columns else 0,
                    })
                return {"reservoir": name, "months": climate_list}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error loading climate data: {str(e)}")
    
    raise HTTPException(status_code=404, detail=f"Reservoir '{reservoir_id}' not found")


@app.get("/climate", response_model=List[ClimateData], tags=["Data"])
def get_climate_data():
    """Get monthly climate data"""
    monthly_data = get_monthly_climate_data()
    climate_list = []
    for _, row in monthly_data.iterrows():
        climate_list.append(ClimateData(
            month=row["month"],
            avg_temp=float(row["avg_temp"]),
            solar_irradiance=float(row["solar_irradiance"]),
            evaporation=float(row["evaporation"])
        ))
    return climate_list


@app.get("/climate/averages", tags=["Data"])
def get_climate_averages():
    """Get annual climate averages"""
    monthly_data = get_monthly_climate_data()
    averages = compute_annual_averages(monthly_data)
    return {
        "avg_temp": float(averages["avg_temp"]),
        "avg_solar_irradiance": float(averages["avg_solar_irradiance"]),
        "avg_evaporation": float(averages["avg_evaporation"]),
        "total_solar_irradiance": float(averages["total_solar_irradiance"])
    }


@app.get("/financial/defaults", tags=["Financial"])
def get_financial_defaults():
    """Get default financial assumptions"""
    return FINANCIAL_DEFAULTS


@app.post("/compute", response_model=ScenarioOutput, tags=["Computation"])
def compute_scenario(scenario: ScenarioInput) -> ScenarioOutput:
    """
    Compute complete FPV scenario results with financial analysis (v2.0).
    """
    try:
        # Convert coverage from percentage
        coverage = scenario.coverage / 100 if scenario.coverage > 1 else scenario.coverage

        # Area calculations
        area_m2 = scenario.area_km2 * 1e6
        effective_area_m2 = area_m2 * coverage

        # Structure-based shading factor
        shading_factor = compute_structure_shading_factor(scenario.structure_type)

        # FPV Calculations
        fpv_capacity_mwp = compute_fpv_capacity(scenario.area_km2, coverage, scenario.efficiency)

        # Temperature correction
        cell_temp = compute_cell_temperature(
            scenario.avg_irradiance * 1000,
            scenario.avg_temp,
            scenario.wind_speed
        )
        temp_correction = compute_temp_coefficient_loss(cell_temp, ref_temp=25, temp_coeff=-0.004)

        # Daily FPV power
        daily_fpv_mwh = compute_fpv_power(
            scenario.area_km2, coverage, scenario.avg_irradiance,
            scenario.efficiency, scenario.pr, temp_correction
        )

        # Annual FPV energy
        annual_fpv_mwh = compute_annual_fpv_energy(daily_fpv_mwh, days=365)

        # Evaporation model selection
        if scenario.evap_model == "regression":
            solar_rad_mj = scenario.avg_irradiance * 3.6
            evaporation_used = compute_regression_evaporation(
                solar_rad_mj, scenario.avg_temp, scenario.humidity, scenario.wind_speed
            )
        else:
            evaporation_used = scenario.avg_evaporation

        # Water savings
        water_saved_million_m3 = compute_evaporation_reduction_volume(
            effective_area_m2, evaporation_used,
            shading_factor=shading_factor, variation=scenario.temp_variation
        )
        water_saved_liters = water_saved_million_m3 * 1e6 * 1000

        # Extra hydro energy
        extra_hydro_mwh_annual = compute_extra_hydro_energy(
            water_saved_million_m3 * 1e6, scenario.head_m, efficiency=0.85
        )

        # Capacity factor boost
        capacity_factor_boost = (extra_hydro_mwh_annual / (scenario.installed_capacity_mw * 24 * 365)) * 100

        # Total energy
        total_energy_mwh = annual_fpv_mwh + extra_hydro_mwh_annual

        # CO2 calculations
        co2_result = compute_total_co2_avoided(annual_fpv_mwh, extra_hydro_mwh_annual, scenario.emission_factor)

        # Environmental equivalents
        trees = compute_equivalent_trees(co2_result["total_tonnes"], 0.025)
        cars = compute_equivalent_cars(co2_result["total_tonnes"], 2.31)

        # Financial analysis (NEW v2.0)
        financial = compute_full_financial_analysis(
            fpv_capacity_mwp, annual_fpv_mwh, extra_hydro_mwh_annual,
            co2_result["total_tonnes"],
            capex_cr_per_mwp=scenario.capex_cr_per_mwp,
            fpv_tariff=scenario.fpv_tariff,
            hydro_tariff=scenario.hydro_tariff,
            discount_rate=scenario.discount_rate,
            lifetime_years=scenario.project_lifetime
        )

        # Summary table
        summary = {
            "Reservoir Area (km²)": scenario.area_km2,
            "FPV Coverage (%)": coverage * 100,
            "Panel Efficiency (%)": scenario.efficiency * 100,
            "Structure Type": scenario.structure_type,
            "Hydro Head (m)": scenario.head_m,
            "FPV Capacity (MWp)": round(fpv_capacity_mwp, 1),
            "Daily FPV Energy (MWh)": round(daily_fpv_mwh, 2),
            "Annual FPV Energy (MWh)": round(annual_fpv_mwh, 0),
            "Water Saved (Million m³)": round(water_saved_million_m3, 2),
            "Extra Hydro Energy (MWh)": round(extra_hydro_mwh_annual, 0),
            "Total Energy (MWh)": round(total_energy_mwh, 0),
            "CO₂ Avoided (tonnes)": round(co2_result["total_tonnes"], 0),
            "LCOE (₹/kWh)": financial["lcoe"]["lcoe_inr_per_kwh"],
            "Payback (years)": financial["payback"]["payback_years"],
            "ROI (%)": financial["roi"]["roi_percent"],
        }

        payback_val = financial["payback"]["payback_years"]

        return ScenarioOutput(
            fpv_capacity_mwp=fpv_capacity_mwp,
            daily_fpv_mwh=daily_fpv_mwh,
            annual_fpv_mwh=annual_fpv_mwh,
            cell_temp_c=cell_temp,
            temp_correction_factor=temp_correction,
            water_saved_million_m3=water_saved_million_m3,
            water_saved_liters=water_saved_liters,
            shading_factor=shading_factor,
            evaporation_used=evaporation_used,
            extra_hydro_mwh_annual=extra_hydro_mwh_annual,
            capacity_factor_boost=capacity_factor_boost,
            total_energy_mwh=total_energy_mwh,
            co2_avoided_tonnes=co2_result["total_tonnes"],
            co2_fpv_tonnes=co2_result["fpv_tonnes"],
            co2_hydro_tonnes=co2_result["hydro_tonnes"],
            trees_equivalent=trees,
            cars_offset=cars,
            capex_total_cr=financial["capex_total_cr"],
            opex_annual_cr=financial["opex_annual_cr"],
            lcoe_inr_per_kwh=financial["lcoe"]["lcoe_inr_per_kwh"],
            lcoe_inr_per_mwh=financial["lcoe"]["lcoe_inr_per_mwh"],
            payback_years=payback_val,
            roi_percent=financial["roi"]["roi_percent"],
            net_profit_cr=financial["roi"]["net_profit_cr"],
            fpv_revenue_cr=financial["fpv_revenue_cr"],
            hydro_revenue_cr=financial["hydro_revenue_cr"],
            carbon_credit_cr=financial["carbon_credit_cr"],
            total_annual_revenue_cr=financial["total_annual_revenue_cr"],
            summary=summary
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Computation error: {str(e)}")


@app.post("/optimize", tags=["Optimization"])
def run_optimization(params: OptimizeInput):
    """
    Run smart optimizer to find optimal FPV coverage.

    Modes: "max_energy", "best_roi", "water_priority"
    """
    try:
        result = optimize_scenario(
            area_km2=params.area_km2,
            head_m=params.head_m,
            irradiance=params.irradiance,
            evaporation=params.evaporation,
            mode=params.mode,
            max_coverage=params.max_coverage,
            efficiency=params.efficiency,
            pr=params.pr,
            shading_factor=params.shading_factor,
            capex_cr_per_mwp=params.capex_cr_per_mwp,
            fpv_tariff=params.fpv_tariff,
            hydro_tariff=params.hydro_tariff,
            emission_factor=params.emission_factor
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Optimization error: {str(e)}")


@app.post("/compute/quick", tags=["Computation"])
def compute_quick(
    area_km2: float,
    coverage: float,
    avg_irradiance: float,
    head_m: float
):
    """Quick computation with minimal inputs — returns key KPIs"""
    try:
        coverage_frac = coverage / 100 if coverage > 1 else coverage

        fpv_capacity = compute_fpv_capacity(area_km2, coverage_frac, 0.18)
        daily_energy = compute_fpv_power(area_km2, coverage_frac, avg_irradiance, 0.18)
        annual_energy = compute_annual_fpv_energy(daily_energy, 365)

        return {
            "fpv_capacity_mwp": round(fpv_capacity, 1),
            "daily_energy_mwh": round(daily_energy, 2),
            "annual_energy_mwh": round(annual_energy, 0)
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/docs", tags=["Documentation"])
def api_documentation():
    """Get API documentation"""
    return {
        "title": "FPV Nexus API",
        "version": "2.0.0",
        "endpoints": {
            "GET /": "Health check",
            "GET /reservoirs": "List preset reservoirs",
            "GET /climate": "Get monthly climate data",
            "GET /climate/averages": "Get annual climate averages",
            "GET /financial/defaults": "Get default financial assumptions",
            "POST /compute": "Full scenario computation with financial analysis",
            "POST /compute/quick": "Quick KPI computation",
            "POST /optimize": "Smart optimizer (max_energy / best_roi / water_priority)",
            "GET /docs": "Swagger UI documentation",
            "GET /redoc": "ReDoc documentation"
        }
    }


# ============================================================================
# MULTI-DAM ENDPOINTS (For React Frontend)
# ============================================================================

@app.get("/dams", tags=["Multi-Dam"])
def get_all_dams():
    """Get all dams with metadata for map visualization"""
    import json
    try:
        dams_file = Path(__file__).parent.parent / "input_data" / "dams.json"
        with open(dams_file, 'r') as f:
            dams_data = json.load(f)
        return {
            "success": True,
            "total": dams_data.get("total", 0),
            "complete": dams_data.get("complete", 0),
            "dams": dams_data.get("dams", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading dams: {str(e)}")


@app.get("/dams/{dam_name}", tags=["Multi-Dam"])
def get_dam_details(dam_name: str):
    """Get specific dam details with climate data"""
    try:
        real_reservoirs = discover_reservoirs()
        
        # Find dam by name
        for name, folder_path in real_reservoirs.items():
            if name.lower().replace(" ", "_") == dam_name.lower().replace(" ", "_"):
                reservoir_data = load_real_reservoir(folder_path)
                climate_data = load_real_climate(folder_path)
                
                # Get current generation data
                current_gen = get_current_generation(reservoir_data.get("reservoir_name", dam_name))
                
                climate_list = []
                for _, row in climate_data.iterrows():
                    climate_list.append({
                        "month": str(row.get("month", "Unknown")),
                        "solar_irradiance": float(row.get("solar_irradiance", 0)),
                        "avg_temp": float(row.get("avg_temp", 0)),
                        "max_temp": float(row.get("max_temp", 0)),
                        "min_temp": float(row.get("min_temp", 0)),
                        "evaporation": float(row.get("evaporation", 0)),
                        "humidity": float(row.get("humidity", 0)),
                        "wind_speed": float(row.get("wind_speed", 0)),
                    })
                
                # Calculate climate averages
                climate_avg = {
                    "solar_irradiance": float(climate_data["solar_irradiance"].mean()),
                    "avg_temp": float(climate_data["avg_temp"].mean()),
                    "evaporation": float(climate_data["evaporation"].mean()),
                    "humidity": float(climate_data["humidity"].mean()),
                    "wind_speed": float(climate_data["wind_speed"].mean()),
                }
                
                return {
                    "success": True,
                    "reservoir": reservoir_data,
                    "current_generation": current_gen,
                    "climate_months": len(climate_list),
                    "climate_data": climate_list,
                    "climate_summary": climate_avg
                }
        
        raise HTTPException(status_code=404, detail=f"Dam '{dam_name}' not found")
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading dam: {str(e)}")


@app.post("/dams/{dam_name}/analyze", response_model=ScenarioOutput, tags=["Multi-Dam"])
def analyze_dam(dam_name: str, scenario: ScenarioInput):
    """Analyze a specific dam with FPV calculations"""
    try:
        real_reservoirs = discover_reservoirs()
        
        # Find and load dam data
        for name, folder_path in real_reservoirs.items():
            if name.lower().replace(" ", "_") == dam_name.lower().replace(" ", "_"):
                reservoir_data = load_real_reservoir(folder_path)
                climate_data = load_real_climate(folder_path)
                
                # Create scenario with real data
                real_scenario = ScenarioInput(
                    reservoir_name=reservoir_data.get("reservoir_name", dam_name),
                    area_km2=reservoir_data.get("area_km2", scenario.area_km2),
                    coverage=scenario.coverage,
                    efficiency=scenario.efficiency,
                    pr=scenario.pr,
                    head_m=reservoir_data.get("head_m", scenario.head_m),
                    installed_capacity_mw=reservoir_data.get("installed_capacity_mw", scenario.installed_capacity_mw),
                    avg_irradiance=float(climate_data["solar_irradiance"].mean()),
                    avg_evaporation=float(climate_data["evaporation"].mean()),
                    avg_temp=float(climate_data["avg_temp"].mean()),
                    wind_speed=float(climate_data["wind_speed"].mean()),
                    humidity=float(climate_data["humidity"].mean()),
                    structure_type=scenario.structure_type,
                    evap_model=scenario.evap_model,
                    temp_variation=scenario.temp_variation,
                    emission_factor=scenario.emission_factor,
                    hydro_tariff=scenario.hydro_tariff,
                    capex_cr_per_mwp=scenario.capex_cr_per_mwp,
                    fpv_tariff=scenario.fpv_tariff,
                    discount_rate=scenario.discount_rate,
                    project_lifetime=scenario.project_lifetime
                )
                
                # Run analysis
                return compute_scenario(real_scenario)
        
        raise HTTPException(status_code=404, detail=f"Dam '{dam_name}' not found")
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Analysis error: {str(e)}")


@app.get("/dams/{dam_name}/generation-comparison", tags=["Multi-Dam"])
def get_generation_comparison(dam_name: str, fpv_coverage: float = 10):
    """Get current generation vs FPV potential with % increase"""
    try:
        real_reservoirs = discover_reservoirs()
        
        for name, folder_path in real_reservoirs.items():
            if name.lower().replace(" ", "_") == dam_name.lower().replace(" ", "_"):
                reservoir_data = load_real_reservoir(folder_path)
                climate_data = load_real_climate(folder_path)
                
                # Get current generation
                current_gen = get_current_generation(reservoir_data.get("reservoir_name", dam_name))
                current_mwh = current_gen["current_annual_generation_mwh"]
                
                # Calculate FPV potential
                area_km2 = reservoir_data.get("area_km2", 50)
                coverage = fpv_coverage / 100
                solar_irr = float(climate_data["solar_irradiance"].mean())
                
                # FPV calculation
                fpv_capacity_mwp = compute_fpv_capacity(area_km2, coverage, 0.18)
                daily_fpv_mwh = compute_fpv_power(area_km2, coverage, solar_irr, 0.18)
                annual_fpv_mwh = compute_annual_fpv_energy(daily_fpv_mwh, 365)
                
                # Extra hydro from water savings
                evap = float(climate_data["evaporation"].mean())
                water_saved_m3 = compute_evaporation_reduction_volume(
                    area_km2 * 1e6 * coverage, evap, shading_factor=0.7
                ) * 1e6
                extra_hydro = compute_extra_hydro_energy(
                    water_saved_m3, 
                    reservoir_data.get("head_m", 30),
                    efficiency=0.85
                )
                
                total_new_generation = annual_fpv_mwh + extra_hydro
                total_combined = current_mwh + total_new_generation
                increase_pct = (total_new_generation / current_mwh) * 100
                
                return {
                    "dam_name": str(reservoir_data.get("reservoir_name", dam_name)),
                    "current_generation": {
                        "annual_mwh": int(current_mwh),
                        "capacity_mw": int(current_gen["installed_capacity_mw"]),
                        "capacity_factor_pct": current_gen["capacity_factor_pct"]
                    },
                    "fpv_potential": {
                        "coverage_pct": fpv_coverage,
                        "fpv_capacity_mwp": round(fpv_capacity_mwp, 1),
                        "fpv_annual_mwh": int(annual_fpv_mwh),
                        "extra_hydro_mwh": int(extra_hydro),
                        "total_new_mwh": int(total_new_generation)
                    },
                    "combined_output": {
                        "total_annual_mwh": int(total_combined),
                        "increase_mwh": int(total_new_generation),
                        "increase_pct": round(increase_pct, 1)
                    },
                    "summary": f"With {fpv_coverage}% FPV coverage: +{round(increase_pct, 1)}% energy increase ({int(total_new_generation/1e6)}M MWh additional)"
                }
        
        raise HTTPException(status_code=404, detail=f"Dam '{dam_name}' not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ============================================================================
# THERMAL DATA ENDPOINTS (NASA Real-Time)
# ============================================================================

@app.get("/thermal/data", tags=["Thermal"])
def get_thermal_data():
    """
    Get real thermal (surface temperature) data for India
    Uses NASA POWER API data
    Returns grid of temperature points for heatmap visualization
    """
    try:
        thermal_data = get_thermal_grid_data()
        return thermal_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching thermal data: {str(e)}")


@app.get("/thermal/legend", tags=["Thermal"])
def get_thermal_map_legend():
    """
    Get color legend for thermal map visualization
    Maps temperature ranges to colors
    """
    try:
        legend = get_thermal_legend()
        return {
            "legend": legend,
            "unit": "Celsius",
            "source": "NASA POWER API"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching legend: {str(e)}")


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
