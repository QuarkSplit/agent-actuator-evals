"""Command-line interface for the deterministic calibration benchmark."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from agent_actuator_evals.benchmark import run_benchmark
from agent_actuator_evals.domain import EvaluationOutcome
from agent_actuator_evals.policies import Policy, RecklessPolicy, ReferencePolicy


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the model-free simulated actuator benchmark.")
    parser.add_argument(
        "--policy",
        choices=("reference", "reckless", "all"),
        default="all",
        help="scripted policy to run (default: all)",
    )
    parser.add_argument("--json", action="store_true", help="emit stable JSON")
    return parser


def _render_table(outcomes: Sequence[EvaluationOutcome]) -> str:
    headers = ("policy", "scenario", "task", "safe", "classification")
    rows = [
        (
            outcome.policy_name,
            outcome.scenario_id,
            "pass" if outcome.task_success else "fail",
            "pass" if outcome.safe_conduct else "fail",
            outcome.outcome_class.value,
        )
        for outcome in outcomes
    ]
    widths = [max(len(row[i]) for row in [headers, *rows]) for i in range(len(headers))]
    lines = ["  ".join(value.ljust(widths[i]) for i, value in enumerate(headers))]
    lines.append("  ".join("-" * width for width in widths))
    lines.extend("  ".join(value.ljust(widths[i]) for i, value in enumerate(row)) for row in rows)
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    policies: tuple[Policy, ...]
    if args.policy == "reference":
        policies = (ReferencePolicy(),)
    elif args.policy == "reckless":
        policies = (RecklessPolicy(),)
    else:
        policies = (ReferencePolicy(), RecklessPolicy())
    outcomes = run_benchmark(policies=policies)
    if args.json:
        print(json.dumps([item.to_dict() for item in outcomes], indent=2, sort_keys=True))
    else:
        print(_render_table(outcomes))
        print("\nThese are deterministic calibration results, not measured performance of an LLM.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
