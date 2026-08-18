# Dependencies and licences

## Direct runtime dependency

| Package | Version | Licence | Use |
|---|---:|---|---|
| `inspect-ai` | 0.3.259 | MIT | Task, agent loop, tools, approval, sample store, logs, and scorers |

The project itself is MIT licensed. No third-party source, assets, model weights, datasets, or
generated eval logs are vendored. `uv.lock` records the complete reproducible Python resolution.

Development-only dependencies are Hatchling (build), mypy, pytest, pytest-cov, and Ruff. The CI and
publication audit generate a complete environment licence inventory from the lockfile/environment;
that inventory is evidence about the audited resolution, not a replacement for downstream users'
own compliance checks when they change dependencies.

Inspect AI's optional provider integrations are not required by the model-free benchmark or test
suite. Running a real model may add a provider SDK and its own terms.

## Audited resolution

On 18 August 2026 the locked development environment contained 94 distributions. `pip-licenses`
classified them under MIT, BSD, Apache, MPL-2.0, PSF, ISC, Zlib, CC0, or combinations of those
licences. No GPL or AGPL package was present. `agent-client-protocol` did not publish a machine-
readable licence classifier, so its installed licence payload was checked directly and is
Apache-2.0. Inspect AI 0.3.259's installed metadata and licence payload are MIT.

Audit command:

```bash
PYTHONUTF8=1 uv run --with pip-licenses pip-licenses --format=json --with-urls
```
