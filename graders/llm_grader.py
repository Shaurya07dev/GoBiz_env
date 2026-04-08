"""
LLM-as-Judge Grader — Qualitative scoring for final recommendations.

Uses the HuggingFace Router (OpenAI-compatible API) to score the agent's
final recommendation on logical structure, evidence usage, and actionability.

Only called once per episode (on the final "recommend" action).
Falls back to rubric score if the LLM call fails.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from typing import Any

logger = logging.getLogger("businessenv")

# Cache: hash(conversation_text) → float
_score_cache: dict[str, float] = {}

EVALUATION_PROMPT = """\
You are an expert business strategy consultant evaluator.

You are evaluating an AI consultant that was given a business case to analyze.
Below is the full conversation between the consultant (agent) and an interviewer.

=== CONVERSATION ===
{conversation}
=== END CONVERSATION ===

=== FINAL RECOMMENDATION ===
{recommendation}
=== END RECOMMENDATION ===

Score the agent's final recommendation on a scale of 0.0 to 1.0 based on:
1. **Logical structure** (0.0–0.35): Is the diagnosis structured and logical?
2. **Use of evidence** (0.0–0.35): Did the agent use facts revealed during the conversation?
3. **Actionability** (0.0–0.30): Are the recommendations specific and actionable?

Return ONLY valid JSON in this exact format (no extra text):
{{"score": 0.75, "reasoning": "Brief explanation of the score"}}
"""


async def score_with_llm(
    conversation_history: list[dict[str, Any]],
    recommendation: str,
    rubric_score: float,
) -> float:
    """Score the agent's final recommendation using an LLM judge.

    Args:
        conversation_history: All turns in the episode.
        recommendation: The agent's final recommendation text.
        rubric_score: Fallback score from the rubric grader.

    Returns:
        Blended score: 0.5 * rubric_score + 0.5 * llm_score. If LLM call
        fails, returns rubric_score unchanged.
    """
    # --- Check cache ---
    conversation_text = _format_conversation(conversation_history)
    cache_key = hashlib.md5(
        (conversation_text + recommendation).encode()
    ).hexdigest()

    if cache_key in _score_cache:
        llm_score = _score_cache[cache_key]
        return 0.5 * rubric_score + 0.5 * llm_score

    # --- Check for API key ---
    hf_token = os.environ.get("HF_TOKEN", "")
    if not hf_token:
        logger.warning("HF_TOKEN not set — skipping LLM grader, using rubric score only.")
        return rubric_score

    # --- Call LLM ---
    try:
        from openai import AsyncOpenAI

        api_base = os.environ.get("API_BASE_URL", "https://router.huggingface.co/v1")
        model = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")

        client = AsyncOpenAI(api_key=hf_token, base_url=api_base)

        prompt = EVALUATION_PROMPT.format(
            conversation=conversation_text,
            recommendation=recommendation,
        )

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a strict scoring evaluator. Return only JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
            max_tokens=200,
        )

        raw_text = response.choices[0].message.content or ""
        llm_score = _parse_llm_score(raw_text)

        # Cache the result
        _score_cache[cache_key] = llm_score

        blended = 0.5 * rubric_score + 0.5 * llm_score
        logger.info(
            f"LLM grader: llm_score={llm_score:.2f}, rubric_score={rubric_score:.2f}, "
            f"blended={blended:.2f}"
        )
        return blended

    except Exception as e:
        logger.warning(f"LLM grader failed ({e}), using rubric score only.")
        return rubric_score


def _format_conversation(history: list[dict[str, Any]]) -> str:
    """Format conversation history into a readable string."""
    lines: list[str] = []
    for turn in history:
        role = turn.get("role", "unknown").upper()
        content = turn.get("content", "")
        lines.append(f"[{role}]: {content}")
    return "\n".join(lines)


def _parse_llm_score(raw_text: str) -> float:
    """Extract the score from the LLM's JSON response.

    Handles common formatting issues: markdown fences, extra whitespace, etc.
    Returns 0.5 as a safe default if parsing fails.
    """
    # Strip markdown code fences if present
    text = raw_text.strip()
    if text.startswith("```"):
        text = "\n".join(text.split("\n")[1:])
    if text.endswith("```"):
        text = "\n".join(text.split("\n")[:-1])
    text = text.strip()

    try:
        data = json.loads(text)
        score = float(data.get("score", 0.5))
        # Clamp to valid range
        return max(0.0, min(1.0, score))
    except (json.JSONDecodeError, TypeError, ValueError):
        logger.warning(f"Could not parse LLM judge response: {raw_text[:200]}")
        return 0.5
