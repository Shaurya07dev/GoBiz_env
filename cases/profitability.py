"""Profitability task helpers."""

from __future__ import annotations

from typing import Any

try:
    from .case_bank import PROFIT_CASES
except ImportError:
    from cases.case_bank import PROFIT_CASES

try:
    from ..utils import match_response
except ImportError:
    from utils import match_response


def get_profitability_cases() -> list[dict[str, Any]]:
    """Return all profitability cases."""
    return PROFIT_CASES


def match_profitability_response(question: str, case: dict[str, Any]) -> str:
    """Match a question to the interviewer response for a profit case."""
    response_bank = case.get("interviewer_response_bank", {})
    response, _ = match_response(question, response_bank)
    return response


def get_rubric_weights() -> dict[str, float]:
    """Return per-rubric-item weights for profitability tasks."""
    return {
        "asked_revenue_vs_cost": 0.06,
        "identified_cost_problem": 0.06,
        "asked_about_timing": 0.06,
        "identified_raw_material_cause": 0.06,
        "identified_freemium_cannibalization": 0.06,
        "identified_cotton_price_cause": 0.06,
        "mentioned_competitor_angle": 0.06,
        "mentioned_cac_issue": 0.06,
        "mentioned_export_decline": 0.06,
        "recommended_pricing_adjustment": 0.06,
        "recommended_cost_optimization": 0.06,
        "recommended_conversion_improvement": 0.06,
        "recommended_supply_contract_strategy": 0.06,
        "recommended_product_mix_shift": 0.06,
        "gave_structured_summary": 0.06,
    }
