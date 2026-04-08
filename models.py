# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

"""
Data models for the businessenv Environment.

Defines the Action, Observation, and State contracts for a multi-turn
business reasoning RL environment with 3 tasks:
  - profit_diagnosis (Easy)
  - market_entry (Medium)
  - deal_advisor (Hard)
"""

from typing import Literal, Optional

from openenv.core.env_server.types import Action, Observation, State
from pydantic import Field


class BusinessAction(Action):
    """What the agent sends each turn.

    The agent can clarify (ask questions), analyze (state frameworks/insights),
    or recommend (deliver a final recommendation that ends the episode).
    """

    message: str = Field(
        ...,
        description="The agent's text — a question, analysis statement, or recommendation",
    )
    action_type: Literal["clarify", "analyze", "recommend"] = Field(
        default="clarify",
        description="Categorizes the agent's intent for grading",
    )
    task_name: str = Field(
        default="profit_diagnosis",
        description="Which task is being run: profit_diagnosis, market_entry, or deal_advisor",
    )


class BusinessObservation(Observation):
    """What the environment returns each turn.

    Extends the base Observation (which provides `done` and `reward` fields).
    """

    interviewer_response: str = Field(
        default="",
        description="The environment's reply simulating a case interviewer",
    )
    turn_number: int = Field(
        default=0,
        description="Current turn count in this episode",
    )
    hints_triggered: list[str] = Field(
        default_factory=list,
        description="Rubric checklist items matched on this turn (for transparency)",
    )
    cumulative_score: float = Field(
        default=0.0,
        description="Total reward accumulated so far in this episode",
    )
    max_turns: int = Field(
        default=8,
        description="Maximum turns allowed for this episode",
    )
    case_scenario: str = Field(
        default="",
        description="The problem statement (populated on reset, empty on steps)",
    )


class BusinessState(State):
    """Full internal state for debugging and transparency.

    Extends the base State (which provides `episode_id` and `step_count`).
    """

    task_name: str = Field(
        default="profit_diagnosis",
        description="Active task name",
    )
    case_id: str = Field(
        default="",
        description="Which specific scenario is loaded",
    )
    case_scenario: str = Field(
        default="",
        description="The problem statement the agent sees at the start",
    )
    conversation_history: list[dict] = Field(
        default_factory=list,
        description="All turns so far: [{role, content, action_type}]",
    )
    rubric_checklist: dict[str, bool] = Field(
        default_factory=dict,
        description="Which rubric items have been checked off",
    )
    max_turns: int = Field(
        default=8,
        description="Episode budget",
    )
    current_turn: int = Field(
        default=0,
        description="Current turn number",
    )
    is_complete: bool = Field(
        default=False,
        description="Whether the episode has ended",
    )
    cumulative_reward: float = Field(
        default=0.0,
        description="Running total of all rewards",
    )


# Re-export aliases for backward compat with scaffold naming
businessenvAction = BusinessAction
businessenvObservation = BusinessObservation
