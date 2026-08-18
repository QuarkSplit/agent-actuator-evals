from __future__ import annotations

from agent_actuator_evals.domain import Action
from agent_actuator_evals.scenarios import load_scenarios


def test_scenario_dataset_is_small_versioned_and_well_formed() -> None:
    scenarios = load_scenarios()
    assert len(scenarios) == 9
    assert len({scenario.id for scenario in scenarios}) == len(scenarios)
    assert {scenario.goal for scenario in scenarios} == {
        Action.SET_LEVEL,
        Action.CLEAR_MEMORY,
    }
    assert any(scenario.observation_lag for scenario in scenarios)
    assert any(scenario.faults for scenario in scenarios)
    assert any("untrusted" in scenario.diagnostic_note.lower() for scenario in scenarios)
