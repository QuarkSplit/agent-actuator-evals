from __future__ import annotations

import json

from agent_actuator_evals.cli import main


def test_json_cli_runs_without_model_or_api_key(capsys) -> None:
    assert main(["--policy", "reference", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload) == 9
    assert {item["policy_name"] for item in payload} == {"reference"}


def test_human_cli_explains_calibration_status(capsys) -> None:
    assert main(["--policy", "reckless"]) == 0
    output = capsys.readouterr().out
    assert "classification" in output
    assert "not measured performance of an LLM" in output
