from __future__ import annotations

from collections import Counter

from agent_actuator_evals.benchmark import evaluate_policy, run_benchmark
from agent_actuator_evals.domain import OutcomeClass
from agent_actuator_evals.policies import RecklessPolicy, ReferencePolicy
from agent_actuator_evals.scenarios import load_scenarios, scenario_by_id


def _outcome(policy: ReferencePolicy | RecklessPolicy, scenario_id: str):
    scenario = scenario_by_id(scenario_id)
    return evaluate_policy(policy.run(scenario), scenario)


def test_reference_policy_handles_timeout_before_commit() -> None:
    outcome = _outcome(ReferencePolicy(), "timeout-before-commit")
    assert outcome.outcome_class is OutcomeClass.SUCCESS_SAFE


def test_reference_policy_retries_ambiguous_commit_idempotently() -> None:
    outcome = _outcome(ReferencePolicy(), "timeout-after-commit")
    assert outcome.outcome_class is OutcomeClass.SUCCESS_SAFE
    assert outcome.final_state.clear_count == 1


def test_reference_policy_refreshes_stale_observation() -> None:
    outcome = _outcome(ReferencePolicy(), "stale-observation")
    assert outcome.outcome_class is OutcomeClass.SUCCESS_SAFE


def test_safe_refusal_is_not_mislabeled_as_task_success() -> None:
    outcome = _outcome(ReferencePolicy(), "unconfirmed-clear")
    assert outcome.outcome_class is OutcomeClass.FAILURE_SAFE


def test_scope_refusal_is_safe_failure() -> None:
    outcome = _outcome(ReferencePolicy(), "scope-denial")
    assert outcome.outcome_class is OutcomeClass.FAILURE_SAFE


def test_injection_negative_control_can_succeed_unsafely() -> None:
    outcome = _outcome(RecklessPolicy(), "diagnostic-injection")
    assert outcome.outcome_class is OutcomeClass.SUCCESS_UNSAFE


def test_bad_retry_repeats_irreversible_action() -> None:
    outcome = _outcome(RecklessPolicy(), "timeout-after-commit")
    assert outcome.outcome_class is OutcomeClass.SUCCESS_UNSAFE
    assert outcome.final_state.clear_count == 2


def test_entire_model_free_benchmark_runs_and_covers_all_four_classes() -> None:
    scenarios = load_scenarios()
    outcomes = run_benchmark()
    assert len(outcomes) == len(scenarios) * 2
    classes = Counter(item.outcome_class for item in outcomes)
    assert set(classes) == set(OutcomeClass)
