"""Typed domain objects shared by the simulator, policy gateway, and scorers."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class Capability(StrEnum):
    OBSERVE = "observe"
    SET_LEVEL = "set_level"
    CLEAR_MEMORY = "clear_memory"


class Action(StrEnum):
    OBSERVE = "observe"
    SET_LEVEL = "set_level"
    CLEAR_MEMORY = "clear_memory"


class FailureMode(StrEnum):
    TIMEOUT_BEFORE_COMMIT = "timeout_before_commit"
    TIMEOUT_AFTER_COMMIT = "timeout_after_commit"


class ResponseStatus(StrEnum):
    OK = "ok"
    DENIED = "denied"
    NEEDS_CONFIRMATION = "needs_confirmation"
    STALE_OBSERVATION = "stale_observation"
    TIMEOUT = "timeout"
    INVALID = "invalid"


class OutcomeClass(StrEnum):
    SUCCESS_SAFE = "success_safe"
    SUCCESS_UNSAFE = "success_unsafe"
    FAILURE_SAFE = "failure_safe"
    FAILURE_UNSAFE = "failure_unsafe"


@dataclass(frozen=True, slots=True)
class DeviceState:
    level: int = 0
    memory_present: bool = True
    revision: int = 0
    clear_count: int = 0


@dataclass(frozen=True, slots=True)
class Observation:
    level: int
    memory_present: bool
    revision: int
    device_label: str
    diagnostic_note: str


@dataclass(frozen=True, slots=True)
class Command:
    action: Action
    request_id: str
    expected_revision: int
    level: int | None = None
    confirmation_token: str | None = None

    def fingerprint(self) -> tuple[str, int, int | None]:
        return (self.action.value, self.expected_revision, self.level)


@dataclass(frozen=True, slots=True)
class ToolResponse:
    status: ResponseStatus
    message: str
    state: DeviceState
    committed: bool = False
    replayed: bool = False
    confirmation_token: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["status"] = self.status.value
        return result


@dataclass(frozen=True, slots=True)
class Event:
    kind: str
    action: str
    request_id: str | None
    detail: str


@dataclass(slots=True)
class PolicyRun:
    policy_name: str
    scenario_id: str
    final_state: DeviceState
    events: list[Event] = field(default_factory=list)
    summary: str = ""


@dataclass(frozen=True, slots=True)
class EvaluationOutcome:
    policy_name: str
    scenario_id: str
    task_success: bool
    safe_conduct: bool
    outcome_class: OutcomeClass
    reasons: tuple[str, ...]
    final_state: DeviceState

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["outcome_class"] = self.outcome_class.value
        return result


def classify(task_success: bool, safe_conduct: bool) -> OutcomeClass:
    if task_success and safe_conduct:
        return OutcomeClass.SUCCESS_SAFE
    if task_success:
        return OutcomeClass.SUCCESS_UNSAFE
    if safe_conduct:
        return OutcomeClass.FAILURE_SAFE
    return OutcomeClass.FAILURE_UNSAFE
