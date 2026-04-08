"""Market entry task helpers."""

from __future__ import annotations

from typing import Any

try:
    from .case_bank import MARKET_ENTRY_CASES
except ImportError:
    from cases.case_bank import MARKET_ENTRY_CASES

try:
    from ..utils import match_response
except ImportError:
    from utils import match_response


def get_market_entry_cases() -> list[dict[str, Any]]:
    """Return all market-entry cases."""
    return MARKET_ENTRY_CASES


def match_market_entry_response(question: str, case: dict[str, Any]) -> str:
    """Match a question to the interviewer response for a market-entry case."""
    response_bank = case.get("interviewer_response_bank", {})
    response, _ = match_response(question, response_bank)
    return response


def get_rubric_weights() -> dict[str, float]:
    """Return per-rubric-item weights for market-entry tasks."""
    return {
        "asked_about_market_size": 0.05,
        "analyzed_competitive_landscape": 0.05,
        "evaluated_company_strengths": 0.05,
        "evaluated_company_weaknesses": 0.05,
        "assessed_financial_viability": 0.05,
        "addressed_regulatory_barriers": 0.05,
        "recommended_entry_mode": 0.05,
        "acknowledged_risks_and_mitigation": 0.05,
        "gave_go_no_go_recommendation": 0.05,
    }
