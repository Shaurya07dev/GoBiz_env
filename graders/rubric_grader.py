"""
Rubric Grader — Deterministic keyword-based scoring.

Provides per-step and final-episode scoring using keyword matching
against task-specific rubric checklists. No external API calls needed.
"""

from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Keyword dictionaries for rubric item detection
# ---------------------------------------------------------------------------

RUBRIC_KEYWORD_MAP: dict[str, list[str]] = {
    # ----- Profitability (shared across profit cases) -----
    "asked_revenue_vs_cost": [
        "revenue", "cost", "profit", "sales", "expense",
        "top line", "bottom line", "income",
    ],
    "identified_cost_problem": [
        "cost increase", "cost problem", "rising cost", "cost went up",
        "cogs", "variable cost", "cost of goods", "margin compress",
        "cost driver", "cost pressure",
    ],
    "asked_about_timing": [
        "when", "how long", "since when", "timeline", "trend",
        "started", "began", "quarter", "month ago",
    ],
    "identified_raw_material_cause": [
        "raw material", "commodity", "coffee bean", "dairy",
        "supply chain", "input cost", "procurement",
    ],
    "identified_cotton_price_cause": [
        "cotton", "raw material", "commodity price", "input cost",
        "harvest", "supply chain", "spot market",
    ],
    "identified_freemium_cannibalization": [
        "freemium", "free tier", "cannibali", "free user",
        "conversion rate", "free plan",
    ],
    "mentioned_competitor_angle": [
        "competitor", "competition", "rival", "new entrant",
        "market share", "competitive pressure",
    ],
    "mentioned_cac_issue": [
        "cac", "customer acquisition cost", "acquisition cost",
        "marketing spend", "ad spend", "google ads",
    ],
    "mentioned_export_decline": [
        "export", "international", "europe", "currency", "rupee",
        "foreign demand", "global",
    ],
    "recommended_pricing_adjustment": [
        "raise price", "increase price", "price hike", "pass on cost",
        "reprice", "premium pricing", "menu price",
    ],
    "recommended_cost_optimization": [
        "reduce cost", "cut cost", "optimize cost", "negotiate",
        "supply contract", "bulk purchas", "cost reduction",
        "operational efficiency",
    ],
    "recommended_conversion_improvement": [
        "improve conversion", "convert free", "upsell", "paywall",
        "freemium to paid", "onboarding funnel", "activation",
    ],
    "recommended_supply_contract_strategy": [
        "long-term contract", "supply agreement", "hedge",
        "lock in price", "forward contract", "supplier",
    ],
    "recommended_product_mix_shift": [
        "product mix", "blended fabric", "diversif", "shift",
        "higher margin product", "portfolio",
    ],
    "gave_structured_summary": [
        "in summary", "to summarize", "recommendation:", "in conclusion",
        "my recommendation", "therefore", "to conclude", "action plan",
        "three steps", "key takeaway",
    ],

    # ----- Market Entry -----
    "asked_about_market_size": [
        "market size", "tam", "addressable", "how big",
        "growth rate", "cagr", "market value", "opportunity",
    ],
    "analyzed_competitive_landscape": [
        "competitor", "competition", "who else", "player",
        "market leader", "incumbent", "fragmented",
    ],
    "evaluated_company_strengths": [
        "strength", "advantage", "core competenc", "capability",
        "distribution", "scale", "brand",
    ],
    "evaluated_company_weaknesses": [
        "weakness", "gap", "lack", "limitation", "challenge",
        "no presence", "no experience",
    ],
    "assessed_financial_viability": [
        "investment", "break even", "roi", "payback",
        "financial", "cost to enter", "capital", "funding",
    ],
    "addressed_regulatory_barriers": [
        "regulat", "compliance", "legal", "license", "permit",
        "certification", "government", "policy",
    ],
    "recommended_entry_mode": [
        "organic", "acquisition", "joint venture", "jv",
        "licensing", "partner", "franchise", "how to enter",
        "entry mode", "go via",
    ],
    "acknowledged_risks_and_mitigation": [
        "risk", "mitigat", "contingency", "downside", "hedge",
        "fallback", "what if", "concern",
    ],
    "gave_go_no_go_recommendation": [
        "go ahead", "proceed", "recommend entry", "should enter",
        "should not enter", "no-go", "advise against",
        "recommendation:", "my recommendation",
    ],

    # ----- Deal Advisor -----
    "clarified_strategic_rationale": [
        "strategic", "rationale", "why acquire", "purpose",
        "objective", "goal of", "motivation",
    ],
    "assessed_financial_health": [
        "ebitda", "burn rate", "cash flow", "runway",
        "profit", "loss", "revenue", "financial health",
        "balance sheet", "debt",
    ],
    "evaluated_market_position": [
        "market position", "market share", "moat",
        "patent", "ip", "intellectual property",
        "competitive advantage",
    ],
    "identified_key_risks": [
        "risk", "key person", "attrition", "retention",
        "patent challenge", "legal risk", "cultural fit",
    ],
    "challenged_valuation": [
        "valuation", "overvalued", "multiple", "13x",
        "comparable", "too expensive", "price fair",
        "premium", "justified",
    ],
    "discussed_synergies": [
        "synergy", "cross-sell", "combined revenue",
        "cost saving", "shared infrastructure",
        "revenue synergy", "cost synergy",
    ],
    "considered_integration_complexity": [
        "integration", "culture", "retention", "attrition",
        "onboarding", "merge team", "culture clash",
    ],
    "assessed_retention_risk": [
        "retention", "attrition", "key person", "talent",
        "competing offer", "non-compete", "lock-in",
        "golden handcuff", "stay bonus",
    ],
    "gave_proceed_recommendation_with_conditions": [
        "proceed with conditions", "recommend acquiring",
        "conditional approval", "advise to proceed",
        "recommendation:", "renegotiate price",
        "should acquire", "my recommendation",
    ],
}


def score_step(
    agent_message: str,
    rubric: dict[str, bool],
    task_name: str,
    conversation_history: list[dict[str, Any]],
) -> tuple[float, list[str]]:
    """Score a single step using keyword matching against the rubric.

    Args:
        agent_message: The agent's text this turn.
        rubric: The current rubric checklist (mutated in place).
        task_name: One of profit_diagnosis, market_entry, deal_advisor.
        conversation_history: Previous turns for repetition detection.

    Returns:
        (reward, newly_triggered_items)
    """
    message_lower = agent_message.lower()
    newly_triggered: list[str] = []
    reward = 0.0

    # --- Check each rubric item ---
    for rubric_key, is_done in list(rubric.items()):
        if is_done:
            continue  # Already triggered

        keywords = RUBRIC_KEYWORD_MAP.get(rubric_key, [])
        if not keywords:
            continue

        if any(kw in message_lower for kw in keywords):
            rubric[rubric_key] = True
            newly_triggered.append(rubric_key)

    # --- Compute reward ---
    # Base reward per new rubric item triggered
    reward_per_item = _get_reward_per_item(task_name)
    reward = len(newly_triggered) * reward_per_item

    # Bonus: specific question (contains ? and a specific term)
    if "?" in agent_message and _has_specificity(message_lower):
        reward += 0.03

    # Cap per-step reward
    reward = min(reward, 0.15)

    return reward, newly_triggered


def score_final(
    rubric: dict[str, bool],
    max_turns: int,
    turns_used: int,
) -> float:
    """Compute the final episode score based on rubric completion.

    Args:
        rubric: The final rubric checklist.
        max_turns: Episode budget.
        turns_used: How many turns the agent took.

    Returns:
        Normalized score in [0.0, 1.0].
    """
    total_items = len(rubric)
    if total_items == 0:
        return 0.0

    completed_items = sum(1 for v in rubric.values() if v)
    rubric_fraction = completed_items / total_items

    # Completion bonus if within step budget
    efficiency_bonus = 0.05 if turns_used <= max_turns else 0.0

    # Final score (capped at 1.0)
    return min(rubric_fraction + efficiency_bonus, 1.0)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _get_reward_per_item(task_name: str) -> float:
    """Return the per-item reward weight based on task difficulty."""
    weights = {
        "profit_diagnosis": 0.06,   # 8 items → ~0.48 from rubric
        "market_entry": 0.05,       # 9 items → ~0.45 from rubric
        "deal_advisor": 0.04,       # 9 items → ~0.36 from rubric
    }
    return weights.get(task_name, 0.05)


def _has_specificity(message_lower: str) -> bool:
    """Check if the message is a specific question (mentions numbers, names, etc.)."""
    # Check for numbers
    if re.search(r"\d+", message_lower):
        return True
    # Check for specific business terms
    specific_terms = [
        "specifically", "exactly", "particular", "which",
        "what percentage", "how much", "how many",
    ]
    return any(term in message_lower for term in specific_terms)
