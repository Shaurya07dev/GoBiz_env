"""
Case Bank — All business scenario definitions for businessenv.

Contains 6 scenarios across 3 tasks:
  - 3 × Profitability Diagnosis (Easy)
  - 2 × Market Entry Analysis  (Medium)
  - 1 × M&A Due Diligence      (Hard)

Each case is a self-contained dict with:
  - problem_statement  (what the agent sees)
  - hidden_facts       (ground truth, never shown)
  - interviewer_response_bank (deterministic replies)
  - rubric             (checklist items, all start False)
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Task 1: Profitability Diagnosis (Easy) — 5-8 turns
# ---------------------------------------------------------------------------

PROFIT_CASES: list[dict[str, Any]] = [
    {
        "case_id": "profit_001",
        "task": "profit_diagnosis",
        "difficulty": "easy",
        "max_turns": 8,
        "problem_statement": (
            "Your client is a mid-size café chain operating 45 outlets across "
            "Tier-1 Indian cities. Over the last 3 quarters, net profit margins "
            "have dropped from 18% to 9%. The CEO has brought you in to diagnose "
            "the issue and recommend a path forward."
        ),
        "hidden_facts": {
            "root_cause": "variable_cost_increase",
            "detail": (
                "Raw material costs (coffee beans, dairy) have risen 30% due to "
                "global supply chain disruptions, but menu prices have not been "
                "adjusted. Additionally, two new competitor chains entered their "
                "top 5 cities in the same period."
            ),
            "secondary_issue": "competitive_pressure",
            "financials": {
                "revenue_change": "-2%",
                "cost_change": "+18%",
                "affected_segment": "premium beverages",
            },
        },
        "interviewer_response_bank": {
            "revenue_question": (
                "Revenue is roughly flat — down about 2% year-over-year. "
                "The decline is spread across most outlets but is steeper "
                "in our top 5 cities."
            ),
            "cost_question": (
                "Yes, costs have risen significantly — primarily variable costs. "
                "Our cost of goods sold has increased by about 18% over the "
                "same period."
            ),
            "time_question": (
                "The margin drop started approximately 9 months ago, coinciding "
                "with the third quarter of last year."
            ),
            "product_question": (
                "Premium beverages are hit the hardest. They account for 40% "
                "of revenue but their margins have compressed from 55% to 35%."
            ),
            "competitor_question": (
                "Yes, two new specialty coffee chains — BeanBrew and CaféCraft — "
                "have opened 12 outlets near our top-performing locations in "
                "Mumbai and Bangalore."
            ),
            "customer_question": (
                "Customer footfall has declined about 8% in cities where "
                "competitors have entered. In other cities, footfall is stable."
            ),
            "pricing_question": (
                "We have not changed our menu prices in the last 18 months. "
                "We were concerned about losing customers if we raised prices."
            ),
            "fixed_cost_question": (
                "Fixed costs like rent and salaries have remained largely stable, "
                "rising only about 3% with annual lease renewals."
            ),
        },
        "rubric": {
            "asked_revenue_vs_cost": False,
            "identified_cost_problem": False,
            "asked_about_timing": False,
            "identified_raw_material_cause": False,
            "mentioned_competitor_angle": False,
            "recommended_pricing_adjustment": False,
            "recommended_cost_optimization": False,
            "gave_structured_summary": False,
        },
    },
    {
        "case_id": "profit_002",
        "task": "profit_diagnosis",
        "difficulty": "easy",
        "max_turns": 8,
        "problem_statement": (
            "Your client is an Indian SaaS startup providing HR management "
            "software to mid-market companies. They have 2,400 paying customers "
            "and monthly revenue of ₹3.2 crore. However, despite a growing user "
            "base, profits have stagnated for 6 months. Diagnose the issue."
        ),
        "hidden_facts": {
            "root_cause": "revenue_mix_shift",
            "detail": (
                "The company introduced a freemium tier 8 months ago which has "
                "cannibalized paid sign-ups. 60% of new users choose the free "
                "tier, and conversion to paid is only 4%. Meanwhile, customer "
                "acquisition cost has risen due to aggressive Google Ads spending."
            ),
            "secondary_issue": "rising_cac",
            "financials": {
                "revenue_change": "+2%",
                "cost_change": "+22%",
                "affected_segment": "customer_acquisition",
            },
        },
        "interviewer_response_bank": {
            "revenue_question": (
                "Revenue has grown very slightly — about 2% over 6 months. "
                "We are adding users but revenue per user has been declining."
            ),
            "cost_question": (
                "Our operating costs have jumped 22%, primarily driven by "
                "marketing spend. Customer acquisition cost is up 40%."
            ),
            "time_question": (
                "Profits plateaued roughly 6 months ago, which is about "
                "2 months after we launched our freemium tier."
            ),
            "product_question": (
                "We launched a free tier with basic features 8 months ago. "
                "60% of new sign-ups choose it. Conversion to paid is around 4%."
            ),
            "competitor_question": (
                "Competition has intensified from players like Zoho People and "
                "Keka HR, who are also offering aggressive free trials."
            ),
            "customer_question": (
                "Our paid customer base of 2,400 is stable but barely growing. "
                "Most growth is in free users who cost us server resources."
            ),
            "pricing_question": (
                "Our paid plans are priced at ₹800/user/month, which is "
                "competitive. We haven't changed pricing recently."
            ),
            "fixed_cost_question": (
                "Infrastructure costs have risen 15% due to the free tier users "
                "consuming server capacity. We added 3 new engineers as well."
            ),
        },
        "rubric": {
            "asked_revenue_vs_cost": False,
            "identified_cost_problem": False,
            "asked_about_timing": False,
            "identified_freemium_cannibalization": False,
            "mentioned_cac_issue": False,
            "recommended_conversion_improvement": False,
            "recommended_cost_optimization": False,
            "gave_structured_summary": False,
        },
    },
    {
        "case_id": "profit_003",
        "task": "profit_diagnosis",
        "difficulty": "easy",
        "max_turns": 8,
        "problem_statement": (
            "Your client is a leading Indian textile manufacturer supplying "
            "fabrics to domestic and export markets. Annual revenue is ₹450 crore. "
            "Over the past 2 quarters, EBITDA margins have fallen from 16% to 8%. "
            "The board needs your diagnosis and recommendations."
        ),
        "hidden_facts": {
            "root_cause": "raw_material_inflation",
            "detail": (
                "Cotton prices have risen 45% globally due to poor harvests in "
                "India and the US. The company's long-term supply contracts expired, "
                "forcing spot-market purchases. Export revenue has also dropped "
                "15% due to a strong rupee and weak European demand."
            ),
            "secondary_issue": "export_revenue_decline",
            "financials": {
                "revenue_change": "-8%",
                "cost_change": "+25%",
                "affected_segment": "raw_materials_and_exports",
            },
        },
        "interviewer_response_bank": {
            "revenue_question": (
                "Total revenue is down about 8%. Domestic revenue is flat, but "
                "export revenue has dropped 15% due to currency headwinds and "
                "weaker demand from European buyers."
            ),
            "cost_question": (
                "Our cost of raw materials — primarily cotton — has increased 45%. "
                "Our long-term supply contracts expired last quarter, and we've "
                "been buying on the spot market at significantly higher prices."
            ),
            "time_question": (
                "The margin decline started 2 quarters ago, coinciding with the "
                "expiry of our cotton supply contracts and the rupee strengthening."
            ),
            "product_question": (
                "Our premium cotton fabrics are worst affected because they are "
                "100% cotton. Our blended fabric lines have held up better since "
                "synthetic inputs are cheaper."
            ),
            "competitor_question": (
                "Competitors with locked-in supply contracts are doing better. "
                "Some have also shifted production to blended fabrics."
            ),
            "customer_question": (
                "Our domestic B2B clients are price-sensitive and have pushed "
                "back on price increases. Two large export clients have reduced "
                "order volumes."
            ),
            "pricing_question": (
                "We've only managed to pass on about 10% of the cost increase "
                "to customers. Further increases risk losing key accounts."
            ),
            "fixed_cost_question": (
                "Fixed costs are stable. We haven't expanded capacity recently. "
                "Depreciation and salaries are in line with budget."
            ),
        },
        "rubric": {
            "asked_revenue_vs_cost": False,
            "identified_cost_problem": False,
            "asked_about_timing": False,
            "identified_cotton_price_cause": False,
            "mentioned_export_decline": False,
            "recommended_supply_contract_strategy": False,
            "recommended_product_mix_shift": False,
            "gave_structured_summary": False,
        },
    },
]

# ---------------------------------------------------------------------------
# Task 2: Market Entry Analysis (Medium) — 8-12 turns
# ---------------------------------------------------------------------------

MARKET_ENTRY_CASES: list[dict[str, Any]] = [
    {
        "case_id": "market_001",
        "task": "market_entry",
        "difficulty": "medium",
        "max_turns": 12,
        "problem_statement": (
            "Your client is an Indian FMCG company (annual revenue ₹5,000 crore) "
            "with a strong presence in soaps and detergents. They are considering "
            "entering the premium personal care market (skincare, serums, sunscreens) "
            "in India. Should they enter? And if so, how?"
        ),
        "hidden_facts": {
            "market_size": "₹18,000 crore growing at 14% CAGR",
            "key_competitors": "Mamaearth, Plum, The Derma Co, L'Oreal India",
            "client_strengths": "Pan-India distribution, manufacturing scale, brand trust",
            "client_weaknesses": "No premium brand equity, limited digital-first capability",
            "recommended_entry_mode": "acquisition_of_d2c_brand",
            "break_even": "18-24 months via acquisition, 36+ months via organic",
        },
        "interviewer_response_bank": {
            "market_size_question": (
                "The Indian premium personal care market is about ₹18,000 crore "
                "and growing at 14% CAGR. D2C brands have captured 25% of this "
                "in just 4 years."
            ),
            "competitor_question": (
                "Key players include Mamaearth (₹1,800 crore revenue), Plum, "
                "The Derma Co (Honasa group), and L'Oreal India. The space is "
                "fragmented with 200+ D2C brands."
            ),
            "company_strengths_question": (
                "Our client has pan-India distribution across 5 million retail "
                "points, strong manufacturing infrastructure, and brand trust "
                "built over 30 years in FMCG."
            ),
            "company_weaknesses_question": (
                "The client lacks premium brand positioning — their existing "
                "brands are perceived as mass-market. They also have limited "
                "digital-first and social media marketing capabilities."
            ),
            "financial_viability_question": (
                "Building a premium brand organically would require ₹300-500 crore "
                "investment over 3 years with break-even at 36+ months. Acquiring "
                "an existing D2C brand could cost ₹500-800 crore but reach "
                "break-even in 18-24 months."
            ),
            "regulatory_question": (
                "FSSAI and BIS certifications are required. Clinical testing for "
                "skincare claims adds 6-12 months. No major regulatory barriers."
            ),
            "entry_mode_question": (
                "Options include: (a) organic brand launch, (b) acquiring a D2C "
                "brand like Plum or mCaffeine, (c) JV with an international "
                "skincare company, (d) licensing an international brand."
            ),
            "risk_question": (
                "Key risks: brand dilution if launched under existing mass-market "
                "umbrella, high customer acquisition costs in digital channels "
                "(₹400-600 per customer), and intense price competition."
            ),
        },
        "rubric": {
            "asked_about_market_size": False,
            "analyzed_competitive_landscape": False,
            "evaluated_company_strengths": False,
            "evaluated_company_weaknesses": False,
            "assessed_financial_viability": False,
            "addressed_regulatory_barriers": False,
            "recommended_entry_mode": False,
            "acknowledged_risks_and_mitigation": False,
            "gave_go_no_go_recommendation": False,
        },
    },
    {
        "case_id": "market_002",
        "task": "market_entry",
        "difficulty": "medium",
        "max_turns": 12,
        "problem_statement": (
            "Your client is an Indian EdTech company (annual revenue ₹800 crore) "
            "offering competitive exam preparation courses. They are considering "
            "expanding into Southeast Asia — specifically Indonesia and Vietnam. "
            "Should they enter? And if so, how?"
        ),
        "hidden_facts": {
            "market_size": "$4.5 billion combined, growing at 18% CAGR",
            "key_competitors": "Ruangguru (Indonesia), Topica (Vietnam), Coursera",
            "client_strengths": "Proven content engine, AI-driven personalization, scale",
            "client_weaknesses": "No local language content, no local brand recognition",
            "recommended_entry_mode": "joint_venture_with_local_player",
            "break_even": "24-30 months",
        },
        "interviewer_response_bank": {
            "market_size_question": (
                "The SEA EdTech market is about $4.5 billion and growing at 18% "
                "CAGR. Indonesia is the largest at $2.8 billion, followed by "
                "Vietnam at $1.2 billion. Penetration is still low at 15%."
            ),
            "competitor_question": (
                "Ruangguru dominates Indonesia with 22 million users. Topica leads "
                "in Vietnam. Coursera and Udemy have English-language presence "
                "but local players are stronger in vernacular content."
            ),
            "company_strengths_question": (
                "Strong content creation pipeline — 10,000+ hours of video content. "
                "Proprietary AI engine for personalized learning paths. "
                "Experience scaling from 100K to 5M users in India."
            ),
            "company_weaknesses_question": (
                "All content is in Hindi and English. Zero brand recognition in SEA. "
                "No local team, no understanding of local exam systems or "
                "curriculum requirements."
            ),
            "financial_viability_question": (
                "Market entry would require $15-20 million over 2 years. "
                "Revenue potential is $30-50 million/year at scale. "
                "Break-even expected in 24-30 months with a JV partner."
            ),
            "regulatory_question": (
                "Indonesia requires local data hosting and Ministry of Education "
                "approval for ed-content. Vietnam has strict content censorship "
                "laws. Both markets require local incorporation."
            ),
            "entry_mode_question": (
                "Options: (a) organic expansion with local hires, (b) JV with "
                "Ruangguru or a local telco, (c) acquire a smaller local EdTech, "
                "(d) license content to local distributors."
            ),
            "risk_question": (
                "Key risks: content localization costs underestimated (₹50-80 crore), "
                "regulatory uncertainty in Vietnam, currency risk (IDR/VND), "
                "and intense local competition with incumbents who have first-mover "
                "advantage."
            ),
        },
        "rubric": {
            "asked_about_market_size": False,
            "analyzed_competitive_landscape": False,
            "evaluated_company_strengths": False,
            "evaluated_company_weaknesses": False,
            "assessed_financial_viability": False,
            "addressed_regulatory_barriers": False,
            "recommended_entry_mode": False,
            "acknowledged_risks_and_mitigation": False,
            "gave_go_no_go_recommendation": False,
        },
    },
]

# ---------------------------------------------------------------------------
# Task 3: M&A Due Diligence — Deal Advisor (Hard) — 12-16 turns
# ---------------------------------------------------------------------------

DEAL_ADVISOR_CASES: list[dict[str, Any]] = [
    {
        "case_id": "deal_001",
        "task": "deal_advisor",
        "difficulty": "hard",
        "max_turns": 16,
        "problem_statement": (
            "Your client is a mid-size Indian IT services company "
            "(annual revenue ₹2,500 crore, 8,000 employees) that is considering "
            "acquiring an AI startup — NeuralForge Labs — for ₹600 crore. "
            "NeuralForge has 120 employees and ₹45 crore in annual revenue. "
            "Conduct a due diligence analysis and advise whether to proceed."
        ),
        "hidden_facts": {
            "strategic_rationale": (
                "The IT company wants to add AI/ML capabilities to compete for "
                "higher-value digital transformation contracts. Their current "
                "AI practice has only 50 engineers."
            ),
            "financial_health": {
                "revenue": "₹45 crore",
                "revenue_growth": "85% YoY",
                "ebitda": "-₹12 crore (loss-making)",
                "burn_rate": "₹3.5 crore/month",
                "cash_runway": "14 months at current burn",
                "debt": "₹8 crore (venture debt)",
            },
            "market_position": {
                "market_share": "2% of Indian enterprise AI market",
                "key_clients": "3 Fortune 500 companies, 8 Indian enterprises",
                "moat": "Proprietary NLP models for Indian languages, 15 patents pending",
            },
            "risks": {
                "key_person_dependency": "CTO and 3 lead researchers are critical",
                "cultural_fit": "Startup culture vs. process-heavy IT services",
                "retention_risk": "40% of engineers have competing offers",
                "ip_risk": "5 patents challenged by a US competitor",
            },
            "valuation_assessment": (
                "At ₹600 crore for ₹45 crore revenue, the price is 13x revenue. "
                "Comparable deals in Indian AI space are 8-10x. Overvalued by "
                "20-30% unless synergies justify the premium."
            ),
            "synergies": {
                "revenue_synergies": "₹200-400 crore/year from AI-enabled contracts",
                "cost_synergies": "₹30-50 crore/year from shared infrastructure",
            },
        },
        "interviewer_response_bank": {
            "strategic_rationale_question": (
                "The acquisition is aimed at building AI/ML capabilities. "
                "Our current AI practice has only 50 engineers and we're losing "
                "bids for digital transformation work worth ₹500+ crore annually."
            ),
            "financial_health_question": (
                "NeuralForge has ₹45 crore revenue, growing 85% YoY. However, "
                "they are loss-making with EBITDA of negative ₹12 crore. "
                "They burn about ₹3.5 crore/month and have 14 months of runway."
            ),
            "revenue_question": (
                "Revenue is ₹45 crore with 85% YoY growth. They have 3 Fortune 500 "
                "clients and 8 Indian enterprise clients. Average contract size "
                "is ₹3-5 crore per year."
            ),
            "market_position_question": (
                "They hold about 2% of the Indian enterprise AI market. "
                "Their moat is proprietary NLP models for Indian languages — "
                "they support 12 languages natively. They have 15 patents pending."
            ),
            "risk_question": (
                "Key risks: (1) CTO and 3 lead researchers are critical to IP — "
                "they don't have non-competes. (2) 40% of engineers have competing "
                "offers from Google, Microsoft, and startups. (3) 5 of their 15 "
                "pending patents are being challenged by a US competitor."
            ),
            "valuation_question": (
                "The asking price of ₹600 crore represents 13x revenue. "
                "Comparable deals in the Indian AI space have been at 8-10x. "
                "The founders argue the premium is justified by their IP and "
                "growth trajectory."
            ),
            "synergy_question": (
                "Revenue synergies: our sales team could cross-sell AI capabilities "
                "to existing clients, potentially adding ₹200-400 crore/year. "
                "Cost synergies: shared cloud infrastructure and back-office "
                "could save ₹30-50 crore/year."
            ),
            "integration_question": (
                "Integration will be complex. NeuralForge has a flat, startup "
                "culture with flexible hours and equity-heavy compensation. "
                "Our company is process-driven with defined hierarchies. "
                "Previous smaller acquisitions faced 30% attrition in Year 1."
            ),
            "competitor_question": (
                "Other IT services companies — Infosys, Wipro, TCS — have all "
                "made AI acquisitions in the ₹200-500 crore range. If we don't "
                "act, NeuralForge may be acquired by a competitor."
            ),
            "legal_question": (
                "There are 5 patent challenges from a US company. The data "
                "rights in 2 client contracts have change-of-control clauses "
                "that need renegotiation. No ongoing litigation otherwise."
            ),
        },
        "rubric": {
            "clarified_strategic_rationale": False,
            "assessed_financial_health": False,
            "evaluated_market_position": False,
            "identified_key_risks": False,
            "challenged_valuation": False,
            "discussed_synergies": False,
            "considered_integration_complexity": False,
            "assessed_retention_risk": False,
            "gave_proceed_recommendation_with_conditions": False,
        },
    },
]


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

ALL_CASES: dict[str, list[dict[str, Any]]] = {
    "profit_diagnosis": PROFIT_CASES,
    "market_entry": MARKET_ENTRY_CASES,
    "deal_advisor": DEAL_ADVISOR_CASES,
}

TASK_MAX_TURNS: dict[str, int] = {
    "profit_diagnosis": 8,
    "market_entry": 12,
    "deal_advisor": 16,
}


def get_cases_for_task(task_name: str) -> list[dict[str, Any]]:
    """Return the list of case dicts for a given task name."""
    if task_name not in ALL_CASES:
        raise ValueError(
            f"Unknown task '{task_name}'. Choose from: {list(ALL_CASES.keys())}"
        )
    return ALL_CASES[task_name]
