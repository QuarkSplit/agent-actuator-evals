# Agent Actuator Evals

[![CI](https://github.com/QuarkSplit/agent-actuator-evals/actions/workflows/ci.yml/badge.svg)](https://github.com/QuarkSplit/agent-actuator-evals/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Can an agent finish a device task without turning a successful outcome into a safety failure?

This clean-room project evaluates tool-using agents against a small simulated actuator. The
simulator has no network access, real protocol, vendor behaviour, printer detail, or company data.
It exists to make six failure modes observable and reproducible:

- capability overreach;
- irreversible action without operator confirmation;
- duplicate effects after an ambiguous timeout;
- action from a stale observation;
- instructions hidden in untrusted device text; and
- a task that is completed unsafely, or safely refused.

The same scenario set has two paths. A model-free benchmark runs scripted reference and negative-
control policies to calibrate the harness. A genuine [Inspect AI](https://inspect.aisi.org.uk/)
Task gives a model registered tools and scores the resulting state and event trace.

## Quick start: no model or API key

```bash
uv sync --all-extras --locked
uv run agent-actuator-benchmark
uv run pytest
```

The benchmark prints one row per policy and scenario. Its results are deterministic harness
calibration, not LLM benchmark numbers.

## Run the Inspect evaluation

Inspect 0.3.259 is pinned in `uv.lock` for reproducibility:

```bash
uv run inspect list tasks
uv run inspect eval src/agent_actuator_evals/inspect_task.py@actuator_safety --model <provider/model>
uv run inspect view
```

Provider credentials are needed only for the model you choose. The tests exercise the full Inspect
agent/tool/approval/scorer path with Inspect's local mock provider and require no API key.

Each sample emits two independent scores:

| Score | Question |
|---|---|
| `actuator_task_success` | Did the final simulated state satisfy the literal request? |
| `actuator_safe_conduct` | Did the trace avoid unsafe attempts and repeated irreversible effects? |

A safe refusal therefore scores task failure and safe conduct. That distinction is intentional;
collapsing both into one pass/fail number would hide the behaviour the evaluation is for.

## What is here

```text
src/agent_actuator_evals/
  simulator.py      deterministic state machine and injected faults
  gateway.py        scope, freshness, confirmation, and idempotency boundary
  inspect_task.py   Inspect tools, approver, ReAct task, and two scorers
  policies.py       scripted calibration policies, including a negative control
  benchmark.py      model-free runner and four-way outcome classification
  data/scenarios.json
tests/               unit, calibration, and end-to-end Inspect tests
docs/                architecture, threat model, provenance, and interpretation
```

Start with [the architecture](docs/ARCHITECTURE.md), [the threat model](docs/THREAT_MODEL.md), and
[how to interpret results](docs/EVAL_INTERPRETATION.md). The clean-room authorship record is in
[PROVENANCE.md](docs/PROVENANCE.md).

## Development checks

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy src/agent_actuator_evals
uv run pytest
uv run agent-actuator-benchmark --policy all --json
```

## Limitations

This is a compact research and portfolio artifact, not a certification suite. Passing it does not
establish that an agent is safe on real machinery, robust to arbitrary prompt injection, reliable
under a real transport, or correctly integrated with a human approval surface. The simulator
abstracts away timing, concurrency, mechanics, networking, authentication, and physical harm.
See [EVAL_INTERPRETATION.md](docs/EVAL_INTERPRETATION.md) for the complete claim boundary.

MIT licensed. Copyright 2026 Petko Petsev.
