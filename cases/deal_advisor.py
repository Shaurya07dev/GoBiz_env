"""Deal advisor task helpers."""

from __future__ import annotations

from typing import Any

try:
    from .case_bank import DEAL_ADVISOR_CASES
except ImportError:
    from cases.case_bank import DEAL_ADVISOR_CASES

try:
    from ..utils import match_response
except ImportError:
    from utils import match_response


def get_deal_advisor_cases() -> list[dict[str, Any]]:
    """Return all deal-advisor cases."""
    return DEAL_ADVISOR_CASES


def match_deal_advisor_response(question: str, case: dict[str, Any]) -> str:
    """Match a question to the interviewer response for a deal-advisor case."""
    response_bank = case.get("interviewer_response_bank", {})
    response, _ = match_response(question, response_bank)
    return response


def get_rubric_weights() -> dict[str, float]:
    """Return per-rubric-item weights for deal-advisor tasks."""
    return {
        "clarified_strategic_rationale": 0.04,
        "assessed_financial_health": 0.04,
        "evaluated_market_position": 0.04,
        "identified_key_risks": 0.04,
        "challenged_valuation": 0.04,
        "discussed_synergies": 0.04,
        "considered_integration_complexity": 0.04,
        "assessed_retention_risk": 0.04,
        "gave_proceed_recommendation_with_conditions": 0.04,
    }
