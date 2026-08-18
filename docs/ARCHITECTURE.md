# Architecture

## Purpose

The project measures two things separately: whether an agent reaches a requested simulated state,
and whether its attempted conduct stays inside a safety policy. The simulator is intentionally too
small to resemble any real device. Its value is that every relevant state transition is explicit,
deterministic, and inspectable.

## Execution path

```text
scenario prompt + authority
          |
          v
  Inspect ReAct agent  ---- scripted calibration policy
          |                         |
          v                         v
 registered tools --------> ActuatorGateway
          |                 scope / freshness / confirmation / idempotency
          |                         |
          |                         v
 Inspect approver --------> SimulatedActuator
                            deterministic state + fault schedule + receipts
                                      |
                                      v
                         final state + append-only events
                                      |
                          +-----------+-----------+
                          v                       v
                    task-success scorer     safe-conduct scorer
```

### Scenario data

`data/scenarios.json` is the versioned benchmark definition. Each sample declares the literal goal,
initial state, exact capability set, whether the simulated operator approves an irreversible
action, initial observation lag, deterministic fault schedule, and untrusted device text.

Authority is data, not prompt text. A sentence claiming to be approval cannot mutate
`operator_approves`.

### Simulator

`SimulatedActuator` is an in-memory state machine. It has a level, a volatile-memory flag, a monotonic
revision, and a count of irreversible clears. A fault queue can produce a timeout before commit or
after commit. The caller receives the same ambiguous timeout in both cases.

Committed commands are recorded against a request id and command fingerprint. An exact retry replays
the receipt. Reusing the id for a different command is rejected. This is the mechanism that makes an
ambiguous retry safe.

### Gateway

`ActuatorGateway` is the domain enforcement point:

1. verify the sample granted the required capability;
2. replay an exact committed request before checking current revision;
3. reject a command based on a stale revision;
4. require an opaque, exact-bound token for `clear_memory`; and
5. execute the simulator command and append an event.

The replay-before-revision order matters. A command that committed and then timed out changed the
revision; its exact retry must return the stored receipt rather than fail as stale.

### Confirmation and Inspect approval

The simulated operator issues a cryptographically opaque capability token from `secrets.token_urlsafe`.
It is bound to action, request id, and observed revision. It is not consumed on first use because an
exact retry after an ambiguous timeout must remain possible. It cannot authorize a new request and
becomes unusable for a new state revision.

Inspect's custom approver checks the same binding before `clear_memory` is dispatched. The gateway
checks again, so direct use outside Inspect has the same safety property. The token material is kept
in sample-scoped internal state. Ordinary observations do not expose it; the model sees it only in
the explicit confirmation response.

The scenario's operator decision is deterministic so benchmark runs are reproducible. This models
the result of a human decision; it is not a claim that a boolean is a real human-in-the-loop system.
A deployment study should replace it with Inspect's `human_approver` or an authenticated external
approval service while retaining the domain binding.

### Scoring

`actuator_task_success` reads the final simulated state. `actuator_safe_conduct` reads the gateway's
event trace and irreversible-action invariant. Neither asks a grader model. The two scores therefore
remain deterministic given a model transcript.

The scripted policies use the same gateway and scorer logic. They are calibration controls, not
substitutes for the Inspect model path.

## Determinism

Scenario selection, initial state, stale reads, fault order, state transitions, and scoring are
deterministic. Opaque confirmation token bytes are deliberately random, but their value does not
affect the outcome. Tests inject a deterministic token source only where they must assert exact
transcript placement.
