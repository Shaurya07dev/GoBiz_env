"""
businessenv Core Environment.

Implements the OpenEnv Environment interface: reset(), step(), state.
Manages multi-turn business reasoning episodes with shaped rewards.
"""

from __future__ import annotations

import asyncio
import copy
import logging
import random
from typing import Any
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment

try:
    from ..models import BusinessAction, BusinessObservation, BusinessState
    from ..cases.case_bank import get_cases_for_task, TASK_MAX_TURNS
    from ..graders import rubric_grader
    from ..graders import llm_grader
    from ..utils import match_response, is_repetitive
except ImportError:
    from models import BusinessAction, BusinessObservation, BusinessState
    from cases.case_bank import get_cases_for_task, TASK_MAX_TURNS
    from graders import rubric_grader
    from graders import llm_grader
    from utils import match_response, is_repetitive

logger = logging.getLogger("businessenv")

ANALYZE_FOLLOWUPS = [
    "That's an interesting framework. What specific data would you like to examine next?",
    "Good analytical approach. Would you like to dig deeper into any particular area?",
    "Solid structure. Do you want to explore any of these branches further?",
    "That's a reasonable decomposition. What aspect would you like to investigate first?",
]


class BusinessEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self) -> None:
        self._state = BusinessState(episode_id=str(uuid4()), step_count=0)
        self._current_case: dict[str, Any] = {}
        self._rubric: dict[str, bool] = {}
        self._conversation_history: list[dict[str, Any]] = []
        self._cumulative_reward: float = 0.0
        self._is_complete: bool = False
        self._task_name: str = "profit_diagnosis"
        self._max_turns: int = 8

    def reset(self, seed: int | None = None, episode_id: str | None = None, **kwargs: Any) -> BusinessObservation:
        self._task_name = kwargs.get("task_name", "profit_diagnosis")
        if seed is not None:
            random.seed(seed)

        cases = get_cases_for_task(self._task_name)
        self._current_case = copy.deepcopy(random.choice(cases))
        self._rubric = copy.deepcopy(self._current_case["rubric"])
        self._max_turns = self._current_case.get(
            "max_turns", TASK_MAX_TURNS.get(self._task_name, 8)
        )

        self._conversation_history = []
        self._cumulative_reward = 0.0
        self._is_complete = False

        self._state = BusinessState(
            episode_id=episode_id or str(uuid4()),
            step_count=0,
            task_name=self._task_name,
            case_id=self._current_case["case_id"],
            case_scenario=self._current_case["problem_statement"],
            conversation_history=[],
            rubric_checklist=copy.deepcopy(self._rubric),
            max_turns=self._max_turns,
            current_turn=0,
            is_complete=False,
            cumulative_reward=0.0,
        )

        return BusinessObservation(
            done=False,
            reward=0.0,
            interviewer_response=self._current_case["problem_statement"],
            turn_number=0,
            hints_triggered=[],
            cumulative_score=0.0,
            max_turns=self._max_turns,
            case_scenario=self._current_case["problem_statement"],
        )

    def step(self, action: BusinessAction, timeout_s: float | None = None, **kwargs: Any) -> BusinessObservation:  # type: ignore[override]
        if self._is_complete:
            return self._terminal_observation("Episode already complete. Call reset().")

        self._state.step_count += 1
        self._state.current_turn += 1
        turn = self._state.current_turn

        message = action.message
        action_type = action.action_type

        self._conversation_history.append({
            "role": "agent",
            "content": message,
            "action_type": action_type,
            "turn": turn,
        })

        step_reward = 0.0
        hints: list[str] = []

        if is_repetitive(message, self._conversation_history[:-1]):
            step_reward -= 0.05
            hints.append("repetition_penalty")

        rubric_reward, triggered = rubric_grader.score_step(
            agent_message=message,
            rubric=self._rubric,
            task_name=self._task_name,
            conversation_history=self._conversation_history,
        )
        step_reward += rubric_reward
        hints.extend(triggered)

        if action_type == "recommend":
            interviewer_response = self._handle_recommendation(message)
            done = True
        elif action_type == "analyze":
            interviewer_response = random.choice(ANALYZE_FOLLOWUPS)
            if not any(
                t.get("action_type") == "analyze"
                for t in self._conversation_history[:-1]
            ):
                step_reward += 0.05
                hints.append("framework_recognition_bonus")
            done = False
        else:
            response_bank = self._current_case.get("interviewer_response_bank", {})
            interviewer_response, _matched_key = match_response(message, response_bank)
            done = False

        if turn >= self._max_turns and not done:
            done = True
            step_reward -= 0.05
            hints.append("max_turns_exceeded_penalty")
            interviewer_response += (
                " We've run out of time. Please deliver your final assessment."
            )

        if done:
            self._is_complete = True
            final_rubric_score = rubric_grader.score_final(
                self._rubric, self._max_turns, turn
            )
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        final_score = pool.submit(
                            asyncio.run,
                            llm_grader.score_with_llm(
                                self._conversation_history, message, final_rubric_score
                            )
                        ).result(timeout=30)
                else:
                    final_score = loop.run_until_complete(
                        llm_grader.score_with_llm(
                            self._conversation_history, message, final_rubric_score
                        )
                    )
            except Exception:
                final_score = final_rubric_score

            step_reward += final_score * 0.4
            hints.append(f"final_score={final_score:.2f}")

        self._cumulative_reward += step_reward

        self._conversation_history.append({
            "role": "interviewer",
            "content": interviewer_response,
            "turn": turn,
        })

        self._state.conversation_history = copy.deepcopy(self._conversation_history)
        self._state.rubric_checklist = copy.deepcopy(self._rubric)
        self._state.is_complete = self._is_complete
        self._state.cumulative_reward = self._cumulative_reward

        return BusinessObservation(
            done=done,
            reward=round(step_reward, 4),
            interviewer_response=interviewer_response,
            turn_number=turn,
            hints_triggered=hints,
            cumulative_score=round(self._cumulative_reward, 4),
            max_turns=self._max_turns,
            case_scenario="",
        )

    @property
    def state(self) -> BusinessState:
        return self._state

    def _handle_recommendation(self, recommendation: str) -> str:
        completed = sum(1 for v in self._rubric.values() if v)
        total = len(self._rubric)
        return (
            f"Thank you for your analysis and recommendation. "
            f"You addressed {completed} out of {total} key areas in your "
            f"investigation. This concludes the case."
        )

    def _terminal_observation(self, message: str) -> BusinessObservation:
        return BusinessObservation(
            done=True,
            reward=0.0,
            interviewer_response=message,
            turn_number=self._state.current_turn,
            hints_triggered=[],
            cumulative_score=round(self._cumulative_reward, 4),
            max_turns=self._max_turns,
            case_scenario="",
        )


__all__ = ["BusinessEnvironment"]
