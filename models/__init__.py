"""
Models package - Computation modules for FPV Nexus Dashboard
Enhanced with Financial Engine, Optimizer, and Advanced Evaporation
"""

from .fpv import (
    compute_fpv_power,
    compute_annual_fpv_energy,
    compute_fpv_capacity,
    compute_cell_temperature,
    compute_temp_coefficient_loss
)

from .evaporation import (
    compute_evaporation_reduction_volume,
    compute_water_savings_liters,
    compute_seasonal_variation,
    compute_uncertainty_range,
    compute_regression_evaporation,
    compute_structure_shading_factor
)

from .hydro import (
    compute_extra_hydro_energy,
    compute_hydro_power_output,
    compute_hydro_capacity_factor,
    compute_revenue_from_hydro,
    estimate_payback_period
)

from .co2 import (
    compute_co2_avoided_fpv,
    compute_co2_avoided_hydro,
    compute_total_co2_avoided,
    compute_equivalent_trees,
    compute_equivalent_cars,
    compute_fuel_oil_equivalent,
    compute_sdg_impact
)

from .financial import (
    compute_lcoe,
    compute_roi,
    compute_payback_with_degradation,
    compute_carbon_credit_value,
    compute_full_financial_analysis,
    DEFAULTS as FINANCIAL_DEFAULTS
)

from .optimizer import (
    optimize_scenario,
    compare_scenarios
)

__all__ = [
    # FPV
    "compute_fpv_power",
    "compute_annual_fpv_energy",
    "compute_fpv_capacity",
    "compute_cell_temperature",
    "compute_temp_coefficient_loss",
    # Evaporation
    "compute_evaporation_reduction_volume",
    "compute_water_savings_liters",
    "compute_seasonal_variation",
    "compute_uncertainty_range",
    "compute_regression_evaporation",
    "compute_structure_shading_factor",
    # Hydro
    "compute_extra_hydro_energy",
    "compute_hydro_power_output",
    "compute_hydro_capacity_factor",
    "compute_revenue_from_hydro",
    "estimate_payback_period",
    # CO2
    "compute_co2_avoided_fpv",
    "compute_co2_avoided_hydro",
    "compute_total_co2_avoided",
    "compute_equivalent_trees",
    "compute_equivalent_cars",
    "compute_fuel_oil_equivalent",
    "compute_sdg_impact",
    # Financial
    "compute_lcoe",
    "compute_roi",
    "compute_payback_with_degradation",
    "compute_carbon_credit_value",
    "compute_full_financial_analysis",
    "FINANCIAL_DEFAULTS",
    # Optimizer
    "optimize_scenario",
    "compare_scenarios",
]
