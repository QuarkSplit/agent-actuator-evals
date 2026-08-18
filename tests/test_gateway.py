from __future__ import annotations

import hashlib

from agent_actuator_evals.domain import Action, ResponseStatus
from agent_actuator_evals.gateway import ActuatorGateway
from agent_actuator_evals.scenarios import scenario_by_id


def test_public_field_hash_cannot_forge_confirmation() -> None:
    scenario = scenario_by_id("confirmed-clear")
    gateway = ActuatorGateway(scenario, token_source=lambda: "test-secret")
    observation = gateway.observe()
    assert observation is not None
    request_id = "clear-1"
    old_public_binding = (
        f"agent-actuator-evals:{Action.CLEAR_MEMORY.value}:{request_id}:{observation.revision}"
    )
    forged = "confirm_" + hashlib.sha256(old_public_binding.encode()).hexdigest()[:24]

    response = gateway.clear_memory(request_id, observation.revision, forged)

    assert response.status is ResponseStatus.NEEDS_CONFIRMATION
    assert gateway.actuator.state.memory_present


def test_confirmation_is_opaque_bound_and_reusable_only_for_idempotent_retry() -> None:
    scenario = scenario_by_id("confirmed-clear")
    gateway = ActuatorGateway(scenario, token_source=lambda: "test-secret")
    observation = gateway.observe()
    assert observation is not None
    confirmation = gateway.request_confirmation(
        Action.CLEAR_MEMORY, "clear-1", observation.revision
    )
    token = confirmation.confirmation_token
    assert token == "confirm_test-secret"

    wrong_request = gateway.clear_memory("clear-2", observation.revision, token)
    assert wrong_request.status is ResponseStatus.NEEDS_CONFIRMATION

    committed = gateway.clear_memory("clear-1", observation.revision, token)
    replayed = gateway.clear_memory("clear-1", observation.revision, token)
    assert committed.status is ResponseStatus.OK
    assert replayed.status is ResponseStatus.OK
    assert replayed.replayed
    assert gateway.actuator.state.clear_count == 1


def test_serialization_preserves_confirmation_without_exposing_it_in_observation() -> None:
    scenario = scenario_by_id("confirmed-clear")
    gateway = ActuatorGateway(scenario, token_source=lambda: "checkpoint-secret")
    observation = gateway.observe()
    assert observation is not None
    token = gateway.request_confirmation(
        Action.CLEAR_MEMORY, "clear-1", observation.revision
    ).confirmation_token

    restored = ActuatorGateway.from_dict(gateway.to_dict(), scenario)
    model_facing_observation = restored.observe()

    assert token is not None
    assert restored.confirmation_valid(token, Action.CLEAR_MEMORY, "clear-1", observation.revision)
    assert model_facing_observation is not None
    assert token not in repr(model_facing_observation)
