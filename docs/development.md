# Development

**Status:** design intent. Finalizes with the build (WBS M0–M24). Milestones live in the
[WBS](wbs/v0.1.0/wbs-v0.1.0-index.md); this guide describes layout, setup, and gates.

## Layout (intended)

```
agentdrill/
  src/agentdrill/         # core: packs, runner, adapters, oracles, evidence, report, cli
  schema/                 # pack JSON Schema
  docs/                   # prd, design, reference, wbs, plans, runbooks, tutorials, guides, ...
  tests/                  # unit, contract, determinism, integration, meta, evasion, field
  Makefile · pyproject.toml
```

## Setup & gates

```sh
make setup          # editable install with dev extras
make test           # pytest + coverage gate (>=95%)
make lint           # ruff, zero violations
make typecheck      # mypy --strict
make drill-self     # ecosystem self-attack (evasion) pack
make benchmark      # regenerate the honest benchmark + heat-map
make verify-release # signatures, manifests, statistical-shape checks
```

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

See the org [CONTRIBUTING](https://github.com/agentsec-ecosystem/.github/blob/main/CONTRIBUTING.md) and
[GOVERNANCE](https://github.com/agentsec-ecosystem/.github/blob/main/GOVERNANCE.md).
