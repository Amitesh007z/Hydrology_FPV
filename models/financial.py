"""
Financial Engine for FPV Nexus
Computes LCOE, ROI, Payback Period, and Carbon Credit Valuation
Based on research paper parameters for Indian FPV installations
"""

import numpy as np


# ============================================================================
# DEFAULT FINANCIAL PARAMETERS (from research literature)
# ============================================================================

DEFAULTS = {
    "capex_cr_per_mwp": 4.0,       # ₹4 Crores per MWp installed
    "opex_percent": 0.02,           # O&M = 2% of CAPEX per year
    "discount_rate": 0.10,          # 10% discount rate
    "project_lifetime_years": 25,   # 25-year project life
    "degradation_rate": 0.005,      # 0.5% panel degradation per year
    "carbon_credit_usd": 5.0,       # $5 per tonne CO₂ (conservative)
    "usd_to_inr": 83.0,            # Exchange rate
}


def compute_lcoe(capex_total_cr, opex_annual_cr, energy_annual_mwh,
                 discount_rate=0.10, lifetime_years=25, degradation_rate=0.005):
    """
    Compute Levelized Cost of Energy (LCOE).

    LCOE = Σ [(I_t + M_t) / (1+r)^t] / Σ [E_t / (1+r)^t]

    Parameters
    ----------
    capex_total_cr : float
        Total capital investment in ₹ Crores
    opex_annual_cr : float
        Annual O&M cost in ₹ Crores
    energy_annual_mwh : float
        First-year annual energy generation in MWh
    discount_rate : float
        Discount rate (0.10 = 10%)
    lifetime_years : int
        Project lifetime in years
    degradation_rate : float
        Annual panel degradation (0.005 = 0.5%)

    Returns
    -------
    dict
        LCOE in ₹/MWh and ₹/kWh
    """
    if energy_annual_mwh <= 0 or lifetime_years <= 0:
        return {"lcoe_inr_per_mwh": float('inf'), "lcoe_inr_per_kwh": float('inf')}

    # Numerator: discounted costs
    cost_npv = capex_total_cr  # Year-0 investment
    for t in range(1, lifetime_years + 1):
        cost_npv += opex_annual_cr / ((1 + discount_rate) ** t)

    # Denominator: discounted energy (with degradation)
    energy_npv = 0.0
    for t in range(1, lifetime_years + 1):
        year_energy = energy_annual_mwh * ((1 - degradation_rate) ** t)
        energy_npv += year_energy / ((1 + discount_rate) ** t)

    # LCOE in ₹ Crores per MWh → convert to ₹/MWh
    lcoe_cr_per_mwh = cost_npv / energy_npv if energy_npv > 0 else float('inf')
    lcoe_inr_per_mwh = lcoe_cr_per_mwh * 1e7  # 1 Crore = 10^7
    lcoe_inr_per_kwh = lcoe_inr_per_mwh / 1000

    return {
        "lcoe_inr_per_mwh": round(lcoe_inr_per_mwh, 2),
        "lcoe_inr_per_kwh": round(lcoe_inr_per_kwh, 2),
    }


def compute_roi(annual_revenue_cr, capex_total_cr, opex_annual_cr, lifetime_years=25):
    """
    Compute Return on Investment over project lifetime.

    ROI = (Total Net Profit / Total Investment) × 100%

    Parameters
    ----------
    annual_revenue_cr : float
        Annual revenue in ₹ Crores (from energy sale + carbon credits)
    capex_total_cr : float
        Total CAPEX in ₹ Crores
    opex_annual_cr : float
        Annual O&M cost in ₹ Crores
    lifetime_years : int
        Project lifetime

    Returns
    -------
    dict
        ROI percentage and total profit
    """
    total_revenue = annual_revenue_cr * lifetime_years
    total_opex = opex_annual_cr * lifetime_years
    total_cost = capex_total_cr + total_opex
    net_profit = total_revenue - total_cost

    roi_percent = (net_profit / capex_total_cr * 100) if capex_total_cr > 0 else 0

    return {
        "roi_percent": round(roi_percent, 1),
        "net_profit_cr": round(net_profit, 2),
        "total_revenue_cr": round(total_revenue, 2),
        "total_cost_cr": round(total_cost, 2),
    }


def compute_payback_with_degradation(capex_total_cr, annual_revenue_cr,
                                      opex_annual_cr, degradation_rate=0.005,
                                      max_years=50):
    """
    Compute payback period factoring in panel degradation and O&M costs.

    Parameters
    ----------
    capex_total_cr : float
        Total CAPEX in ₹ Crores
    annual_revenue_cr : float
        First-year annual revenue in ₹ Crores
    opex_annual_cr : float
        Annual O&M cost in ₹ Crores
    degradation_rate : float
        Annual revenue degradation (0.005 = 0.5%)
    max_years : int
        Maximum years to search

    Returns
    -------
    dict
        Payback period and cumulative cash flow
    """
    if annual_revenue_cr <= opex_annual_cr:
        return {"payback_years": float('inf'), "cumulative_cashflow_cr": -capex_total_cr}

    cumulative = -capex_total_cr
    for year in range(1, max_years + 1):
        year_revenue = annual_revenue_cr * ((1 - degradation_rate) ** year)
        net_cashflow = year_revenue - opex_annual_cr
        cumulative += net_cashflow

        if cumulative >= 0:
            # Interpolate within the year for fractional payback
            prev_cumulative = cumulative - net_cashflow
            fraction = -prev_cumulative / net_cashflow if net_cashflow > 0 else 0
            payback = year - 1 + fraction
            return {
                "payback_years": round(payback, 1),
                "cumulative_cashflow_cr": round(cumulative, 2),
            }

    return {"payback_years": float('inf'), "cumulative_cashflow_cr": round(cumulative, 2)}


def compute_carbon_credit_value(co2_tonnes, credit_price_usd=5.0, usd_to_inr=83.0):
    """
    Estimate revenue from carbon credits.

    Parameters
    ----------
    co2_tonnes : float
        Annual CO₂ avoided in tonnes
    credit_price_usd : float
        Price per tonne of CO₂ credit in USD
    usd_to_inr : float
        Exchange rate

    Returns
    -------
    dict
        Annual carbon credit revenue in ₹ Crores and USD
    """
    revenue_usd = co2_tonnes * credit_price_usd
    revenue_inr = revenue_usd * usd_to_inr
    revenue_cr = revenue_inr / 1e7

    return {
        "annual_usd": round(revenue_usd, 2),
        "annual_inr_cr": round(revenue_cr, 4),
    }


def compute_full_financial_analysis(fpv_capacity_mwp, annual_fpv_mwh,
                                     extra_hydro_mwh, co2_tonnes,
                                     capex_cr_per_mwp=4.0, opex_percent=0.02,
                                     fpv_tariff=3.5, hydro_tariff=4.5,
                                     discount_rate=0.10, lifetime_years=25,
                                     degradation_rate=0.005,
                                     carbon_credit_usd=5.0, usd_to_inr=83.0):
    """
    Run complete financial analysis combining all metrics.

    Parameters
    ----------
    fpv_capacity_mwp : float
        Installed FPV capacity in MWp
    annual_fpv_mwh : float
        Annual FPV energy in MWh
    extra_hydro_mwh : float
        Annual extra hydro energy in MWh
    co2_tonnes : float
        Annual CO₂ avoided
    capex_cr_per_mwp : float
        CAPEX per MWp in ₹ Crores
    opex_percent : float
        O&M as fraction of CAPEX
    fpv_tariff : float
        FPV energy tariff ₹/kWh (converted internally)
    hydro_tariff : float
        Hydro energy tariff ₹/kWh (converted internally)
    discount_rate : float
        Discount rate
    lifetime_years : int
        Project lifetime
    degradation_rate : float
        Annual panel degradation
    carbon_credit_usd : float
        Carbon credit price per tonne (USD)
    usd_to_inr : float
        Exchange rate

    Returns
    -------
    dict
        Complete financial analysis results
    """
    # CAPEX & OPEX
    capex_total_cr = fpv_capacity_mwp * capex_cr_per_mwp
    opex_annual_cr = capex_total_cr * opex_percent

    # Revenue streams
    # fpv_tariff is in ₹/kWh → convert to ₹/MWh (×1000), then to Crores (÷1e7)
    fpv_revenue_cr = (annual_fpv_mwh * fpv_tariff * 1000) / 1e7
    # hydro_tariff is in ₹/kWh → convert to ₹/MWh (×1000), then to Crores (÷1e7)
    hydro_revenue_cr = (extra_hydro_mwh * hydro_tariff * 1000) / 1e7
    carbon = compute_carbon_credit_value(co2_tonnes, carbon_credit_usd, usd_to_inr)

    total_annual_revenue_cr = fpv_revenue_cr + hydro_revenue_cr + carbon["annual_inr_cr"]

    # LCOE
    total_annual_mwh = annual_fpv_mwh + extra_hydro_mwh
    lcoe = compute_lcoe(capex_total_cr, opex_annual_cr, total_annual_mwh,
                        discount_rate, lifetime_years, degradation_rate)

    # ROI
    roi = compute_roi(total_annual_revenue_cr, capex_total_cr, opex_annual_cr, lifetime_years)

    # Payback
    payback = compute_payback_with_degradation(capex_total_cr, total_annual_revenue_cr,
                                                opex_annual_cr, degradation_rate)

    return {
        "capex_total_cr": round(capex_total_cr, 2),
        "opex_annual_cr": round(opex_annual_cr, 2),
        "fpv_revenue_cr": round(fpv_revenue_cr, 4),
        "hydro_revenue_cr": round(hydro_revenue_cr, 4),
        "carbon_credit_cr": carbon["annual_inr_cr"],
        "total_annual_revenue_cr": round(total_annual_revenue_cr, 4),
        "lcoe": lcoe,
        "roi": roi,
        "payback": payback,
    }
