"""Deterministic in-memory actuator with injected timing and freshness faults."""

from __future__ import annotations

from collections import deque
from dataclasses import asdict
from typing import Any

from agent_actuator_evals.domain import (
    Action,
    Command,
    DeviceState,
    FailureMode,
    Observation,
    ResponseStatus,
    ToolResponse,
)
from agent_actuator_evals.scenarios import Scenario


class SimulatedTimeout(Exception):
    """A controlled timeout whose commit state is intentionally ambiguous to the caller."""

    def __init__(self, *, committed: bool) -> None:
        super().__init__("simulated transport timeout")
        self.committed = committed


class IdempotencyCollision(Exception):
    """A request id was reused for a different command."""


class SimulatedActuator:
    """A vendor-neutral device model. It never opens a socket or touches real hardware."""

    def __init__(self, scenario: Scenario) -> None:
        revision = 1 if scenario.observation_lag else 0
        self.state = DeviceState(level=scenario.initial_level, revision=revision)
        self.device_label = scenario.device_label
        self.diagnostic_note = scenario.diagnostic_note
        older = DeviceState(level=scenario.initial_level, revision=0)
        self._history = [older, self.state] if revision else [self.state]
        self._stale_reads_remaining = scenario.observation_lag
        self._faults: deque[FailureMode] = deque(scenario.faults)
        self._fault_action = scenario.goal
        self._receipts: dict[str, tuple[tuple[str, int, int | None], ToolResponse]] = {}

    def observe(self) -> Observation:
        if self._stale_reads_remaining > 0 and len(self._history) > 1:
            self._stale_reads_remaining -= 1
            observed = self._history[-2]
        else:
            observed = self.state
        return Observation(
            level=observed.level,
            memory_present=observed.memory_present,
            revision=observed.revision,
            device_label=self.device_label,
            diagnostic_note=self.diagnostic_note,
        )

    def replay(self, command: Command) -> ToolResponse | None:
        receipt = self._receipts.get(command.request_id)
        if receipt is None:
            return None
        fingerprint, response = receipt
        if fingerprint != command.fingerprint():
            raise IdempotencyCollision(command.request_id)
        return ToolResponse(
            status=response.status,
            message="replayed stored result for the same request id",
            state=response.state,
            committed=response.committed,
            replayed=True,
        )

    def execute(self, command: Command) -> ToolResponse:
        replay = self.replay(command)
        if replay is not None:
            return replay

        fault = self._next_fault(command.action)
        if fault is FailureMode.TIMEOUT_BEFORE_COMMIT:
            raise SimulatedTimeout(committed=False)

        if command.action is Action.SET_LEVEL:
            if command.level is None or not 0 <= command.level <= 10:
                return ToolResponse(
                    ResponseStatus.INVALID,
                    "level must be between 0 and 10",
                    self.state,
                )
            self.state = DeviceState(
                level=command.level,
                memory_present=self.state.memory_present,
                revision=self.state.revision + 1,
                clear_count=self.state.clear_count,
            )
        elif command.action is Action.CLEAR_MEMORY:
            self.state = DeviceState(
                level=self.state.level,
                memory_present=False,
                revision=self.state.revision + 1,
                clear_count=self.state.clear_count + 1,
            )
        else:
            return ToolResponse(ResponseStatus.INVALID, "unsupported command", self.state)

        self._history.append(self.state)
        response = ToolResponse(
            ResponseStatus.OK,
            "command committed",
            self.state,
            committed=True,
        )
        self._receipts[command.request_id] = (command.fingerprint(), response)
        if fault is FailureMode.TIMEOUT_AFTER_COMMIT:
            raise SimulatedTimeout(committed=True)
        return response

    def _next_fault(self, action: Action) -> FailureMode | None:
        if action is self._fault_action and self._faults:
            return self._faults.popleft()
        return None

    def to_dict(self) -> dict[str, Any]:
        receipts: dict[str, Any] = {}
        for request_id, (fingerprint, response) in self._receipts.items():
            receipts[request_id] = {
                "fingerprint": list(fingerprint),
                "response": response.to_dict(),
            }
        return {
            "state": asdict(self.state),
            "device_label": self.device_label,
            "diagnostic_note": self.diagnostic_note,
            "history": [asdict(item) for item in self._history],
            "stale_reads_remaining": self._stale_reads_remaining,
            "faults": [item.value for item in self._faults],
            "fault_action": self._fault_action.value,
            "receipts": receipts,
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> SimulatedActuator:
        instance = cls.__new__(cls)
        instance.state = DeviceState(**value["state"])
        instance.device_label = str(value["device_label"])
        instance.diagnostic_note = str(value["diagnostic_note"])
        instance._history = [DeviceState(**item) for item in value["history"]]
        instance._stale_reads_remaining = int(value["stale_reads_remaining"])
        instance._faults = deque(FailureMode(item) for item in value["faults"])
        instance._fault_action = Action(value["fault_action"])
        instance._receipts = {}
        for request_id, receipt in value["receipts"].items():
            raw_fingerprint = receipt["fingerprint"]
            fingerprint = (
                str(raw_fingerprint[0]),
                int(raw_fingerprint[1]),
                int(raw_fingerprint[2]) if raw_fingerprint[2] is not None else None,
            )
            raw_response = receipt["response"]
            response = ToolResponse(
                status=ResponseStatus(raw_response["status"]),
                message=str(raw_response["message"]),
                state=DeviceState(**raw_response["state"]),
                committed=bool(raw_response["committed"]),
                replayed=bool(raw_response["replayed"]),
            )
            instance._receipts[str(request_id)] = (fingerprint, response)
        return instance
