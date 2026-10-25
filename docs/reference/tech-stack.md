# Tech Stack

**Status:** built (v0.1.0).

## Runtime

| Layer | Choice |
|---|---|
| Core | **Python 3.10+** — library + CLI wrapper + pytest-style API; one engine, three surfaces (DD-15) |
| Packaging | `pyproject.toml`; PyPI `agentsec-agentdrill`; console script `agentdrill` (DD-17) |
| Pack format | YAML primary, JSON secondary (DD-16) |
| Evidence | **agentwatch** record + security-event schema (consumed, not forked — DD-05) |

## Quality gates

| Gate | Tool |
|---|---|
| Lint | `ruff` (zero violations) |
| Types | `mypy --strict` |
| Tests | `pytest`; coverage **≥ 95%** |
| Signing | Sigstore (packs, manifests, results) |
| SBOM | CycloneDX |
| Supply chain | DCO, dependency review, OpenSSF baseline |

## Storage

- Local-first JSON under `.agentdrill/` (DD-19); no database required for core function.
- Audit log append-only, rotated, hash-chained.

## Seams

- **agentwatch** — record + security-event schema (telemetry/evidence).
- **agentpolicy / policyweave** — compiled policy + kill-time budgets (targets).
- **agentgate / agentkeys / agentseatbelt / agentkernel / agenthalt** — enforcement targets.
- **agentcomply** — compliance evidence consumer.
