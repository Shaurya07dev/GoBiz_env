#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
businessenv Inference Script — Baseline Agent.

Runs an LLM agent (via HuggingFace Router / OpenAI-compatible API) against
all 3 businessenv tasks and prints mandatory [START]/[STEP]/[END] logs.

Environment variables:
    HF_TOKEN        — HuggingFace API token (required)
    API_BASE_URL    — LLM API base URL (default: https://router.huggingface.co/v1)
    MODEL_NAME      — Model identifier (default: Qwen/Qwen2.5-72B-Instruct)

Usage:
    HF_TOKEN=hf_xxx python inference.py
    # or with uv:
    HF_TOKEN=hf_xxx uv run inference.py
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time

from openai import OpenAI

# Add project root to path so imports work when run standalone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.businessenv_environment import BusinessEnvironment
from models import BusinessAction, BusinessObservation

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("inference")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TASKS = ["profit_diagnosis", "market_entry", "deal_advisor"]
MAX_STEPS_PER_TASK = {"profit_diagnosis": 8, "market_entry": 12, "deal_advisor": 16}

CONSULTANT_SYSTEM_PROMPT = """\
You are a business strategy consultant. You are given a client's business problem.
Your job is to:
1. Ask targeted clarifying questions to diagnose the problem (use action_type: "clarify")
2. Identify the root cause using business frameworks (use action_type: "analyze")
3. Deliver a structured recommendation (use action_type: "recommend")

IMPORTANT:
- Ask one question at a time
- Be specific and use business terminology
- Base your analysis only on information you have been given
- Do NOT make assumptions without asking
- When you are ready to recommend, start your message with "RECOMMENDATION:"
- Your response MUST contain 2-4 clarification/analysis turns before recommending

Respond in JSON format:
{"message": "your text here", "action_type": "clarify|analyze|recommend"}
"""


def run_episode(
    env: BusinessEnvironment,
    client: OpenAI,
    model: str,
    task_name: str,
) -> dict:
    """Run a single episode for the given task.

    Returns:
        Dict with keys: task, steps, score, rewards, success
    """
    max_steps = MAX_STEPS_PER_TASK.get(task_name, 8)

    # Reset environment
    obs = env.reset(task_name=task_name)
    case_scenario = obs.case_scenario or obs.interviewer_response

    # Build conversation for LLM
    conversation = [
        {"role": "system", "content": CONSULTANT_SYSTEM_PROMPT},
        {"role": "user", "content": f"Here is the case:\n\n{case_scenario}"},
    ]

    print(f"[START] task={task_name} env=businessenv model={model}")

    total_rewards: list[float] = []
    step_num = 0
    done = False

    while not done and step_num < max_steps:
        # Ask LLM for next action
        try:
            response = client.chat.completions.create(
                model=model,
                messages=conversation,
                temperature=0.7,
                max_tokens=300,
            )
            agent_text = response.choices[0].message.content or ""
        except Exception as e:
            logger.warning(f"LLM call failed: {e}")
            agent_text = '{"message": "Can you tell me more about the situation?", "action_type": "clarify"}'

        # Parse JSON from agent response
        try:
            parsed = _parse_agent_json(agent_text)
            action = BusinessAction(
                message=parsed["message"],
                action_type=parsed.get("action_type", "clarify"),
                task_name=task_name,
            )
        except Exception:
            # Fallback: treat entire text as a clarify action
            clean_text = agent_text.strip()
            if clean_text.upper().startswith("RECOMMENDATION"):
                action_type = "recommend"
            else:
                action_type = "clarify"
            action = BusinessAction(
                message=clean_text,
                action_type=action_type,
                task_name=task_name,
            )

        # Step the environment
        obs = env.step(action)
        step_num += 1
        done = obs.done
        reward = obs.reward or 0.0
        total_rewards.append(reward)

        # Add to LLM conversation
        conversation.append({"role": "assistant", "content": action.message})
        conversation.append({"role": "user", "content": obs.interviewer_response})

        error = "null"
        print(
            f"[STEP] step={step_num} action={action.action_type} "
            f"reward={reward:.2f} done={str(done).lower()} error={error}"
        )

    # Compute final score
    cumulative = sum(total_rewards)
    # Normalize to [0, 1] — max possible is roughly 1.0
    final_score = min(max(cumulative, 0.0), 1.0)
    rewards_str = ",".join(f"{r:.2f}" for r in total_rewards)
    success = final_score >= 0.1

    print(
        f"[END] success={str(success).lower()} steps={step_num} "
        f"score={final_score:.2f} rewards={rewards_str}"
    )
    print()

    return {
        "task": task_name,
        "steps": step_num,
        "score": final_score,
        "rewards": total_rewards,
        "success": success,
    }


def _parse_agent_json(text: str) -> dict:
    """Extract JSON from agent response, handling markdown fences."""
    text = text.strip()

    # Remove markdown code fences
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:])
    if text.endswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[:-1])
    text = text.strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON object in the text
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not parse JSON from: {text[:200]}")


def main():
    """Main entry point — runs all 3 tasks in sequence."""
    hf_token = os.environ.get("HF_TOKEN", "")
    if not hf_token:
        print("ERROR: HF_TOKEN environment variable is required.", file=sys.stderr)
        print("Set it with: $env:HF_TOKEN='hf_your_token_here'", file=sys.stderr)
        sys.exit(1)

    api_base = os.environ.get("API_BASE_URL", "https://router.huggingface.co/v1")
    model = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")

    client = OpenAI(api_key=hf_token, base_url=api_base)

    print(f"=== businessenv Inference ===")
    print(f"Model: {model}")
    print(f"API Base: {api_base}")
    print(f"Tasks: {', '.join(TASKS)}")
    print()

    results = []
    start_time = time.time()

    for task in TASKS:
        env = BusinessEnvironment()
        result = run_episode(env, client, model, task)
        results.append(result)

    elapsed = time.time() - start_time

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for r in results:
        status = "✓" if r["success"] else "✗"
        print(f"  {status} {r['task']:20s} → score={r['score']:.2f} steps={r['steps']}")
    avg_score = sum(r["score"] for r in results) / len(results) if results else 0
    print(f"\n  Average score: {avg_score:.2f}")
    print(f"  Total time: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
