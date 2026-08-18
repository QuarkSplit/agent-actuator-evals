"""Load and validate the small, versioned benchmark scenario set."""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib.resources import files
from typing import Any

from agent_actuator_evals.domain import Action, Capability, FailureMode


@dataclass(frozen=True, slots=True)
class Scenario:
    id: str
    prompt: str
    goal: Action
    initial_level: int
    target_level: int | None
    capabilities: frozenset[Capability]
    operator_approves: bool
    observation_lag: int
    faults: tuple[FailureMode, ...]
    device_label: str
    diagnostic_note: str

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Scenario:
        goal = Action(str(value["goal"]))
        target = value.get("target_level")
        return cls(
            id=str(value["id"]),
            prompt=str(value["prompt"]),
            goal=goal,
            initial_level=int(value.get("initial_level", 0)),
            target_level=int(target) if target is not None else None,
            capabilities=frozenset(Capability(item) for item in value["capabilities"]),
            operator_approves=bool(value.get("operator_approves", False)),
            observation_lag=int(value.get("observation_lag", 0)),
            faults=tuple(FailureMode(item) for item in value.get("faults", [])),
            device_label=str(value.get("device_label", "sim-actuator-a")),
            diagnostic_note=str(value.get("diagnostic_note", "nominal")),
        )


def load_scenarios() -> tuple[Scenario, ...]:
    resource = files("agent_actuator_evals.data").joinpath("scenarios.json")
    payload = json.loads(resource.read_text(encoding="utf-8"))
    scenarios = tuple(Scenario.from_dict(item) for item in payload)
    ids = [scenario.id for scenario in scenarios]
    if len(ids) != len(set(ids)):
        raise ValueError("scenario ids must be unique")
    return scenarios


def scenario_by_id(scenario_id: str) -> Scenario:
    return next(s for s in load_scenarios() if s.id == scenario_id)
