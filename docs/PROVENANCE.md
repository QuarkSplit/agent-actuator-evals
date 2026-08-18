# Clean-room provenance

## Origin

This repository was created from a blank directory on 18 August 2026 as a personal public project by
Petko Petsev with AI-assisted implementation. The problem statement was specified at the level of
general safety properties: scoped tools, confirmation for irreversible actions, idempotency,
timeouts, stale observations, adversarial requests, and separate success/safety outcomes.

The domain, state machine, scenarios, prompts, tests, documentation, and naming were written for this
repository. No employer or customer repository, source file, schema, prompt, screenshot, trace,
protocol, operational data, or private session artifact was read, copied, adapted, or published.
The simulated actuator is deliberately generic and cannot connect to real hardware.

## Public sources consulted

- [Inspect AI documentation](https://inspect.aisi.org.uk/), especially Tasks, custom tools, stateful
  tools, scorers, agents, and tool approval.
- [Inspect AI source repository](https://github.com/UKGovernmentBEIS/inspect_ai), MIT licensed, to
  verify the current public extension interfaces.
- [Inspect AI on PyPI](https://pypi.org/project/inspect-ai/) to select and pin the current release.

Inspect AI is used as a dependency through its documented API. No Inspect source is vendored or
copied into this repository.

## Authorship boundary

The public history begins with this clean-room implementation. A full-tree and full-history secret/
PII scan is required before publication. The repository's only intended personal identifiers are
Petko Petsev, London, UK, `petko.petzev@gmail.com`, and `github.com/QuarkSplit`.
