# Development

**Status:** layout, setup, and gates. The tree was **ported from the predecessor eval harness at WBS M0**
(provenance: [THIRD_PARTY_NOTICES](../THIRD_PARTY_NOTICES.md); plan: [M0 port](plans/m0-port-execution-plan.md));
later milestones re-point the mechanics from agent-quality grading to defense proof. Milestones live in the
[WBS](wbs/v0.1.0/wbs-v0.1.0-index.md).

## Layout

```
agentdrill/
  src/agentdrill/         # core: packs, runner, adapters, oracles, evidence, report, cli
  tests/                  # unit, contract, integration, determinism, fixtures
  scenarios/              # curated scenario packs (YAML)
  schemas/                # run-result JSON schemas
  examples/               # demo agents + adversarial pack
  field/                  # field harness (real-agent runs; not product evidence)
  scripts/                # tooling: docker tests, smoke, secret-scan, template verify
  schema/                 # pack JSON Schema
  docs/                   # prd, design, reference, wbs, plans, runbooks, tutorials, guides, ...
  pyproject.toml · agentdrill.toml · Dockerfile
```

## Ported tree (M0)

M0 imported the predecessor's `src/`, `tests/`, `scenarios/`, `schemas/`, `examples/`, `field/`, tooling, and
the non-colliding docs subset as a single import commit, renamed the package to `agentdrill`, reset the version
to **0.1.0**, and removed all predecessor-name references (only the provenance notes may name the source — a
guard test enforces this). No behavior was rewritten at M0; the ported suite is green.

## Setup & gates

```sh
uv venv && uv pip install -e '.[dev]'          # editable install with dev extras
.venv/bin/python -m pytest -m "not docker and not omlx"   # unit suite (docker/omlx run separately)
ruff check .                                    # lint, zero violations
mypy                                            # mypy --strict
```

`docker`/`omlx`-marked tests need a Docker daemon / a local oMLX server and run in their own jobs. A `make`
front-end for these targets lands in M1.

## Workflow (one ticket at a time)

1. Write the test for the feature (RED).
2. Implement (GREEN).
3. Next ticket — **do not** run the full suite between tickets.
4. At **milestone end**: run the gates once (full suite, coverage, ruff, mypy), commit, push, close the
   issue, record a checkpoint.

## Definition of done

Implemented + tests passing + committed + pushed + tracking issue closed. Anything else is not done and is
reported as such.

## Quality gate

`ruff` zero · `mypy --strict` clean · coverage **≥ 95%**. Enforced in CI ([tech-stack](reference/tech-stack.md)).

## Contributing

See the org [CONTRIBUTING](https://github.com/agentic-suite/.github/blob/main/CONTRIBUTING.md) and
[GOVERNANCE](https://github.com/agentic-suite/.github/blob/main/GOVERNANCE.md).
