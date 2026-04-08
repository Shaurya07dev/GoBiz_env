"""
Shared utilities for businessenv.

Provides:
  - Keyword-based response matching (maps an agent question to the best
    interviewer response from the case's response bank)
  - Text similarity helpers
  - Logging helpers
"""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger("businessenv")

# ---------------------------------------------------------------------------
# Response keyword dictionaries — maps response_bank key → trigger keywords
# ---------------------------------------------------------------------------

RESPONSE_KEYWORDS: dict[str, list[str]] = {
    "revenue_question": [
        "revenue", "sales", "income", "turnover", "top line",
        "top-line", "growth rate", "revenue trend",
    ],
    "cost_question": [
        "cost", "expense", "margin", "overhead", "variable cost",
        "fixed cost", "cogs", "cost of goods", "operating cost",
        "expenditure", "spend",
    ],
    "time_question": [
        "when", "how long", "since when", "timeline", "trend",
        "quarter", "year", "month", "started", "began", "duration",
    ],
    "product_question": [
        "product", "segment", "category", "line", "sku",
        "offering", "portfolio", "service", "solution",
    ],
    "competitor_question": [
        "competitor", "competition", "rival", "market share",
        "alternative", "peer", "benchmark", "competitive",
    ],
    "customer_question": [
        "customer", "client", "user", "footfall", "retention",
        "churn", "acquisition", "buyer", "consumer", "base",
    ],
    "pricing_question": [
        "price", "pricing", "premium", "discount", "rate",
        "fee", "tariff", "charge", "menu price",
    ],
    "fixed_cost_question": [
        "fixed cost", "rent", "salary", "depreciation", "lease",
        "overhead", "admin", "fixed expense",
    ],
    # Market entry / deal advisor specific
    "market_size_question": [
        "market size", "tam", "sam", "addressable", "market value",
        "growth rate", "cagr", "market opportunity", "how big",
    ],
    "company_strengths_question": [
        "strength", "advantage", "core competenc", "capability",
        "what are we good at", "moat", "differentiat",
    ],
    "company_weaknesses_question": [
        "weakness", "limitation", "gap", "what we lack",
        "disadvantage", "challenge", "shortcoming",
    ],
    "financial_viability_question": [
        "financial viability", "break even", "breakeven", "roi",
        "return on investment", "npv", "investment required",
        "how much will it cost", "payback",
    ],
    "regulatory_question": [
        "regulat", "compliance", "legal", "license", "permit",
        "government", "policy", "certification", "fssai", "bis",
    ],
    "entry_mode_question": [
        "entry mode", "how to enter", "organic", "acquisition",
        "joint venture", "jv", "licensing", "franchise", "partner",
    ],
    "risk_question": [
        "risk", "threat", "danger", "downside", "concern",
        "what could go wrong", "barrier",
    ],
    # Deal advisor specific
    "strategic_rationale_question": [
        "strategic", "rationale", "why acquire", "purpose",
        "objective", "goal", "motivation", "reason for",
    ],
    "financial_health_question": [
        "financial health", "ebitda", "burn rate", "cash flow",
        "runway", "profitab", "balance sheet", "debt",
    ],
    "market_position_question": [
        "market position", "market share", "competitive moat",
        "patent", "ip", "intellectual property",
    ],
    "valuation_question": [
        "valuation", "price", "multiple", "revenue multiple",
        "worth", "fair value", "overvalued", "undervalued",
        "how much", "what price",
    ],
    "synergy_question": [
        "synergy", "synergies", "cross-sell", "cross sell",
        "combined", "integration benefit", "value creation",
    ],
    "integration_question": [
        "integration", "culture", "onboarding", "retention",
        "attrition", "merge", "combine team",
    ],
    "legal_question": [
        "legal", "litigation", "lawsuit", "contract clause",
        "change of control", "ip dispute", "patent challenge",
    ],
}

# Default fallback response
DEFAULT_RESPONSE = (
    "Could you be more specific about what aspect of the business you'd "
    "like to explore? I can share details about revenue, costs, market "
    "dynamics, competition, or other areas."
)


def match_response(
    agent_message: str,
    response_bank: dict[str, str],
) -> tuple[str, str | None]:
    """Match an agent question to the best interviewer response.

    Uses keyword overlap scoring — the response bank key whose keyword list
    has the most matches in the agent message wins.

    Args:
        agent_message: The agent's question or statement.
        response_bank: The case's interviewer_response_bank dict.

    Returns:
        A tuple of (interviewer_response, matched_key_or_None).
    """
    message_lower = agent_message.lower()

    best_key: str | None = None
    best_score: int = 0

    for response_key in response_bank:
        keywords = RESPONSE_KEYWORDS.get(response_key, [])
        score = sum(1 for kw in keywords if kw in message_lower)
        if score > best_score:
            best_score = score
            best_key = response_key

    if best_key and best_score > 0:
        return response_bank[best_key], best_key
    return DEFAULT_RESPONSE, None


def normalize_text(text: str) -> str:
    """Lowercase, strip, collapse whitespace."""
    return re.sub(r"\s+", " ", text.strip().lower())


def is_repetitive(
    message: str,
    conversation_history: list[dict[str, Any]],
    threshold: float = 0.6,
) -> bool:
    """Check if the agent's message is too similar to a previous message.

    Uses a simple word-overlap Jaccard coefficient.
    """
    msg_words = set(normalize_text(message).split())
    if not msg_words:
        return False

    for turn in conversation_history:
        if turn.get("role") != "agent":
            continue
        prev_words = set(normalize_text(turn.get("content", "")).split())
        if not prev_words:
            continue
        intersection = msg_words & prev_words
        union = msg_words | prev_words
        if union and len(intersection) / len(union) >= threshold:
            return True
    return False
