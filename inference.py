#!/usr/bin/env python3
# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Inference Script Example
===================================
MANDATORY
- Before submitting, ensure the following variables are defined in your environment configuration:
    API_BASE_URL   The API endpoint for the LLM.
    MODEL_NAME     The model identifier to use for inference.
    HF_TOKEN       Your Hugging Face / API key.
    LOCAL_IMAGE_NAME The name of the local image to use for the environment if you are using from_docker_image()
                     method

- Defaults are set only for API_BASE_URL and MODEL_NAME
    (and should reflect your active inference setup), for example:
    API_BASE_URL = os.getenv("API_BASE_URL", "<your-active-endpoint>")
    MODEL_NAME = os.getenv("MODEL_NAME", "<your-active-model>")
    (This repo uses the Hugging Face router URL and Qwen model as the default
    second arguments so `uv run inference.py` works when env vars are unset.)

- The inference script must be named `inference.py` and placed in the root directory of the project
- Participants must use OpenAI Client for all LLM calls using above variables

STDOUT FORMAT
- The script must emit exactly three line types to stdout, in this order:

    [START] task=<task_name> env=<benchmark> model=<model_name>
    [STEP]  step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
    [END]   success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>

  Rules:
    - One [START] line at episode begin.
    - One [STEP] line per step, immediately after env.step() returns.
    - One [END] line after env.close(), always emitted (even on exception).
    - reward and rewards are formatted to 2 decimal places.
    - done and success are lowercase booleans: true or false.
    - error is the raw last_action_error string, or null if none.
    - All fields on a single line with no newlines within a line.
    - Each tasks should return score in [0, 1]

  Example:
    [START] task=click-test env=miniwob model=Qwen3-VL-30B
    [STEP] step=1 action=click('123') reward=0.00 done=false error=null
    [STEP] step=2 action=fill('456','text') reward=0.00 done=false error=null
    [STEP] step=3 action=click('789') reward=1.00 done=true error=null
    [END] success=true steps=3 score=1.00 rewards=0.00,0.00,1.00
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import textwrap
from typing import Any, List, Optional

from openai import OpenAI
from openenv.core.client_types import StepResult

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from businessenv.client import BusinessEnv
    from businessenv.models import BusinessAction, BusinessObservation
    from businessenv.server.businessenv_environment import BusinessEnvironment
except ImportError:
    from client import BusinessEnv
    from models import BusinessAction, BusinessObservation
    from server.businessenv_environment import BusinessEnvironment

# ---------------------------------------------------------------------------
# Environment configuration (MANDATORY pattern)
# ---------------------------------------------------------------------------

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")
# Optional compatibility with some setups (not required by rubric)
API_KEY = os.getenv("API_KEY")
# Optional — if you use from_docker_image(); also accept IMAGE_NAME for compatibility
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME") or os.getenv("IMAGE_NAME")

BENCHMARK = os.getenv("BUSINESSENV_BENCHMARK", "businessenv")

TASKS = ["profit_diagnosis", "market_entry", "deal_advisor"]
MAX_STEPS_PER_TASK = {"profit_diagnosis": 8, "market_entry": 12, "deal_advisor": 16}

TEMPERATURE = 0.7
MAX_TOKENS = 300
SUCCESS_SCORE_THRESHOLD = 0.1

CONSULTANT_SYSTEM_PROMPT = textwrap.dedent(
    """
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
).strip()


def log_start(task: str, env_name: str, model: str) -> None:
    print(f"[START] task={task} env={env_name} model={model}", flush=True)


def log_step(
    step: int,
    action: str,
    reward: float,
    done: bool,
    error: Optional[str],
) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


def _action_repr(action: BusinessAction) -> str:
    """Single-line action string for structured logs (no embedded newlines)."""
    payload = {"message": action.message.replace("\n", " ").replace("\r", " "), "action_type": action.action_type}
    return json.dumps(payload, ensure_ascii=False)


class _LocalAsyncEnv:
    """Wraps sync BusinessEnvironment for async inference flow."""

    def __init__(self) -> None:
        self._env = BusinessEnvironment()

    async def reset(self, **kwargs: Any):
        obs: BusinessObservation = await asyncio.to_thread(self._env.reset, **kwargs)
        return StepResult(
            observation=obs,
            reward=obs.reward,
            done=obs.done,
        )

    async def step(self, action: BusinessAction, **kwargs: Any):
        obs: BusinessObservation = await asyncio.to_thread(self._env.step, action)
        return StepResult(
            observation=obs,
            reward=obs.reward,
            done=obs.done,
        )

    async def close(self) -> None:
        return None


async def _make_env():
    if LOCAL_IMAGE_NAME:
        return await BusinessEnv.from_docker_image(LOCAL_IMAGE_NAME)
    return _LocalAsyncEnv()


def _parse_agent_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:])
    if text.endswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[:-1])
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        return json.loads(text[start:end])
    raise ValueError("Could not parse JSON from model output")


def get_model_action(
    client: OpenAI,
    conversation: list[dict[str, str]],
    task_name: str,
) -> BusinessAction:
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=conversation,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        agent_text = (completion.choices[0].message.content or "").strip()
    except Exception as exc:
        err = str(exc)
        if len(err) > 400:
            err = err[:400] + "..."
        print(f"[DEBUG] Model request failed: {err}", flush=True, file=sys.stderr)
        agent_text = '{"message": "Can you tell me more about the situation?", "action_type": "clarify"}'

    try:
        parsed = _parse_agent_json(agent_text)
        return BusinessAction(
            message=parsed["message"],
            action_type=parsed.get("action_type", "clarify"),
            task_name=task_name,
        )
    except Exception:
        clean_text = agent_text.strip()
        if clean_text.upper().startswith("RECOMMENDATION"):
            action_type = "recommend"
        else:
            action_type = "clarify"
        return BusinessAction(
            message=clean_text,
            action_type=action_type,
            task_name=task_name,
        )


async def run_episode(
    env,
    client: OpenAI,
    task_name: str,
) -> None:
    max_steps = MAX_STEPS_PER_TASK.get(task_name, 8)
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False
    log_start(task=task_name, env_name=BENCHMARK, model=MODEL_NAME)

    try:
        try:
            result = await env.reset(task_name=task_name)
        except Exception as exc:
            print(f"[DEBUG] env.reset() failed: {exc}", flush=True, file=sys.stderr)
        else:
            obs = result.observation
            case_scenario = obs.case_scenario or obs.interviewer_response

            conversation: list[dict[str, str]] = [
                {"role": "system", "content": CONSULTANT_SYSTEM_PROMPT},
                {"role": "user", "content": f"Here is the case:\n\n{case_scenario}"},
            ]

            for step_num in range(1, max_steps + 1):
                if result.done:
                    break

                action = get_model_action(client, conversation, task_name)
                step_error: Optional[str] = None
                try:
                    result = await env.step(action)
                except Exception as exc:
                    step_error = str(exc)
                    result = StepResult(observation=obs, reward=0.0, done=False)

                obs = result.observation
                reward = float(result.reward if result.reward is not None else 0.0)
                done = bool(result.done)
                rewards.append(reward)
                steps_taken = step_num

                log_step(
                    step=step_num,
                    action=_action_repr(action),
                    reward=reward,
                    done=done,
                    error=step_error,
                )

                conversation.append({"role": "assistant", "content": action.message})
                conversation.append({"role": "user", "content": obs.interviewer_response})

                if done:
                    break

            cumulative = sum(rewards)
            score = min(max(cumulative, 0.0), 1.0)
            success = score >= SUCCESS_SCORE_THRESHOLD

    finally:
        try:
            await env.close()
        except Exception as exc:
            print(f"[DEBUG] env.close() error: {exc}", flush=True, file=sys.stderr)
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


async def main_async() -> None:
    api_key = HF_TOKEN or API_KEY or ""
    client = OpenAI(base_url=API_BASE_URL, api_key=api_key)

    for task_name in TASKS:
        env = await _make_env()
        await run_episode(env, client, task_name)


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
