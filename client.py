# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""businessenv Environment Client."""

from typing import Dict

from openenv.core import EnvClient
from openenv.core.client_types import StepResult

from .models import BusinessAction, BusinessObservation, BusinessState


class BusinessEnv(
    EnvClient[BusinessAction, BusinessObservation, BusinessState]
):
    """
    Client for the businessenv Environment.

    Maintains a persistent WebSocket connection to the environment server.

    Example:
        >>> with BusinessEnv(base_url="http://localhost:8000") as client:
        ...     result = client.reset()
        ...     print(result.observation.interviewer_response)
        ...
        ...     result = client.step(BusinessAction(
        ...         message="What has happened to revenue?",
        ...         action_type="clarify",
        ...         task_name="profit_diagnosis"
        ...     ))
        ...     print(result.observation.interviewer_response)
    """

    def _step_payload(self, action: BusinessAction) -> Dict:
        """Convert BusinessAction to JSON payload for step message."""
        return {
            "message": action.message,
            "action_type": action.action_type,
            "task_name": action.task_name,
        }

    def _parse_result(self, payload: Dict) -> StepResult[BusinessObservation]:
        """Parse server response into StepResult[BusinessObservation]."""
        obs_data = payload.get("observation", {})
        observation = BusinessObservation(
            interviewer_response=obs_data.get("interviewer_response", ""),
            turn_number=obs_data.get("turn_number", 0),
            hints_triggered=obs_data.get("hints_triggered", []),
            cumulative_score=obs_data.get("cumulative_score", 0.0),
            max_turns=obs_data.get("max_turns", 8),
            case_scenario=obs_data.get("case_scenario", ""),
            done=payload.get("done", False),
            reward=payload.get("reward"),
        )

        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> BusinessState:
        """Parse server response into BusinessState object."""
        return BusinessState(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
            task_name=payload.get("task_name", ""),
            case_id=payload.get("case_id", ""),
            case_scenario=payload.get("case_scenario", ""),
            conversation_history=payload.get("conversation_history", []),
            rubric_checklist=payload.get("rubric_checklist", {}),
            max_turns=payload.get("max_turns", 8),
            current_turn=payload.get("current_turn", 0),
            is_complete=payload.get("is_complete", False),
            cumulative_reward=payload.get("cumulative_reward", 0.0),
        )
