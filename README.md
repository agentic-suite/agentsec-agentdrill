# agentdrill

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyPI](https://img.shields.io/badge/pypi-agentsec--agentdrill-blue.svg)](https://pypi.org/project/agentsec-agentdrill/)
[![Status: v0.1.0](https://img.shields.io/badge/status-v0.1.0%20(in%20progress)-yellow.svg)](docs/prd/09-roadmap.md)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy strict](https://img.shields.io/badge/mypy-strict-blue.svg)](https://github.com/python/mypy)
[![Docs](https://img.shields.io/badge/docs-PRD%2000--24-blue.svg)](docs/prd/README.md)

> **Prove** — Reproducible attack packs run in CI against your *deployed* agent-defense stack, with
> honest, published results — including the attacks we did **not** stop.

[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/agentsec-ecosystem/agentdrill/badge)](https://scorecard.dev/viewer/?uri=github.com/agentsec-ecosystem/agentdrill)

Part of the [agentsec-ecosystem](https://github.com/agentsec-ecosystem) — open-source,
harness-agnostic security for AI agents.

**Status: v0.1.0 — in progress.** The foundation has landed: the ported engine (M0) and the CLI,
fail-closed configuration, CI quality gate, and identity docs (M1). The proof engine is wired
end-to-end at M18; the [PRD](docs/prd/README.md) is the design of record. The intent is published early,
on purpose, so we can be held to it.

---

## Install & Quick Start

```sh
# Install (PyPI)
pip install agentsec-agentdrill        # Python CLI + SDK (import + CLI: agentdrill)
agentdrill --help                      # list commands

# First run in ~15 minutes, against a bundled demo stack (no real stack required)
agentdrill quickstart

# Drill your own deployed stack
agentdrill run --pack replit-destructive-command --target ./my-stack.yaml --sandbox

# Gate a policy change in CI — a rule that un-blocks an attack is rejected
agentdrill run --pack incidents-core --target ./stack.yaml --ci

# Verify a published result with nothing installed
agentdrill verify ./benchmark-release.json
```

The proof loop: **pick a pack → point at your deployed stack → run locally or in CI → read an honest
result** (`blocked` / `missed` / `degraded`) **+ kill-time**. See [PRD 04](docs/prd/04-users-and-cujs.md).

### See it before installing

Run `agentdrill quickstart` to boot a **static, bundled demo stack** and produce a first drill report —
one pack's honest outcome split, a kill-chain timeline, and an exportable evidence bundle. It runs
offline, opens from `file://`, needs no account, and is pure synthetic data watermarked
**`demo — never evidence`**.

---

## Why

Every agent-security vendor oversells detection, and almost nobody publishes reproducible evidence of
what their controls actually stop. The benchmark record is brutal: simple prompt injection retains
**~46% ASR** against some of the best-known defenses, and one hacking prompt nearly **doubles** ASR
against GPT-4 ReAct agents. Meanwhile red-team tooling (PyRIT, garak, promptfoo, AgentDojo) is strong
but **offline and point-in-time** — it red-teams a snapshot, not a live policy stack.

Nothing treats agent **policies as continuously regression-tested code**. `agentdrill` is that layer:
the ecosystem's proof-of-work engine. See [PRD 01](docs/prd/01-why.md).

## What it does

| Capability | Description |
|---|---|
| Attack packs | Curated, versioned **incident-replay** packs (Replit destructive-command, MCP tool poisoning, Plugin4Shell supply-chain, Slack-AI exfil, credential evasion) |
| Runs the deployed stack | Drives the **real** enforcement path (MCP proxy, credential broker, confinement, compiled policy, halt) — never a simulation |
| Honest results | Every published table includes the **misses**; no scoring theater |
| Kill-time verification | Times revocation to actual **cessation** (probed, not inferred) — a full kill-chain timeline, not one latency |
| CI gate | A policy PR that un-blocks a known attack is **rejected** before merge |
| Public benchmark | Reproducible per-release results — a third party re-runs and gets the same numbers |
| Efficacy control | A `blocked` number only counts if the attack demonstrably succeeds **unguarded** (the control group no one else runs) |
| Evasion pack | Attacks on the ecosystem **itself** (tamper, hook-disable, policy-edit, telemetry-injection) run every release |
| Interop | Import promptfoo / garak / AgentDojo / PyRIT suites — don't reinvent |
| Standards-tagged | Every pack mapped to MITRE ATLAS + OWASP (LLM + Agentic) |
| Harness-agnostic | Works across harnesses by construction, or ships named per-harness packs |

## Honest by design

This is the differentiator, so it is enforced, not aspirational ([PRD 07](docs/prd/07-success-metrics.md),
[PRD 20](docs/prd/20-efficacy-freshness-lifecycle.md)):

- **Misses are first-class** — a run cannot publish without them.
- **A single run is never a claim** — published numbers are mean ± std over ≥3 pinned seeds; kill-time
  reports p50/p95/max.
- **Contamination is disclosed, not hidden** — cases overlapping a judge/target model's training data are
  flagged in the table.
- **Flag, never silently fix** — expected outcomes are preregistered; a change is *flagged* with a re-pin
  note.
- **Disputes get answered** — a public adjudication process with a 14-day SLA on every published finding.

## Compatibility

A harness is "compatible" only when **its pack passes in CI**; release notes carry the compatibility
table ([PRD 05](docs/prd/05-features.md) §Compatibility).

| Tier | Harness | Support |
|---|---|---|
| 1 — Coding agents | Claude Code · Cursor · GitHub Copilot · Codex CLI · Gemini CLI | ≥2 at v0.1.0 (per-harness packs) |
| 2 — Frameworks | LangGraph · CrewAI · OpenAI Agents SDK · AutoGen/AG2 · LlamaIndex · PydanticAI · smolagents | via promptfoo/garak interop; adapter packs in scope |
| 3 — Protocol/enterprise | Generic MCP clients · enterprise platforms | MCP-layer coverage via agentgate; enterprise via standards |

## Security & supply chain

- **Signed packs + provenance** on every release ([PRD 17](docs/prd/17-pack-registry-and-governance.md)).
- **Trust levels** (`built-in` / `local` / `external`) — external packs are sandbox-restricted, never
  used for benchmark results.
- **Target attestation** (`live` / `fixture` / `mock`) — results are labeled at the weakest link; `mock`
  never publishes.
- **Standalone verifier** — a zero-install, offline check of signatures, hashes, manifests, and labels;
  a bundle is verified on a machine that never ran the drill.
- **Evidence privacy** — target-side secrets redacted before bundling, with verifiable redaction receipts.
- **Self-audit** — the evasion pack is the sanctioned way we attack ourselves; **disclosure** per
  [SECURITY.md](./SECURITY.md).

## Verification & quality gates

```sh
make setup            # create the venv + install dev extras
make lint             # ruff, zero violations
make typecheck        # mypy --strict
make test             # functional test suite (excludes docker/omlx infra tests)
make cov              # functional suite with the coverage gate (>=95%)
make test-all         # full suite incl. docker/omlx (needs a daemon + oMLX server)
```

> Self-attack, benchmark, and release-verification targets (`drill-self` / `benchmark` /
> `verify-release`) land with their milestones (M14 / M10 / M32).

- Published benchmark: honest outcome split per release, **misses included**
  ([PRD 07](docs/prd/07-success-metrics.md)).
- Every published number is efficacy-backed and multi-seed; every row links its traces
  ([PRD 19](docs/prd/19-detection-validation-bas.md)).

## Development

Python core (`pack format`, `runner`, `driver`/`target` adapters, `oracle` engine, reporter, registry),
CLI wrapper, and a pytest-style API — one engine, every surface ([PRD 02](docs/prd/02-architecture.md)).

```sh
make setup        # editable install with dev extras
agentdrill list packs        # discover packs / oracles / targets / drivers
agentdrill run --dry-run --pack incidents-core --target ./stack.yaml
agentdrill quickstart        # end-to-end against the bundled demo stack
```

## Documentation

Full index: [docs/prd/README.md](docs/prd/README.md).

**Why & scope**

- [Press Release / FAQ](docs/prd/00-press-release.md) · [Why](docs/prd/01-why.md) · [Landscape](docs/prd/03-landscape.md) · [Non-Goals](docs/prd/14-non-goals.md)

**How it works**

- [Architecture](docs/prd/02-architecture.md) · [Data Model](docs/prd/15-data-model.md) · [Kill-Chain Verification](docs/prd/18-kill-chain-verification.md) · [Attack-Chain Orchestration](docs/prd/16-attack-chain-orchestration.md)

**What ships**

- [What (Features)](docs/prd/05-features.md) · [Pack Catalog](docs/prd/21-pack-catalog.md) · [Detection Validation & BAS-Class](docs/prd/19-detection-validation-bas.md) · [Frontier & DX](docs/prd/22-frontier-dx-features.md)

**Trust**

- [Security Baseline](docs/prd/06-security-baseline.md) · [Success Metrics](docs/prd/07-success-metrics.md) · [Efficacy, Freshness & Lifecycle](docs/prd/20-efficacy-freshness-lifecycle.md) · [Oracle Credibility](docs/prd/23-oracle-credibility.md)

**Users, parity & governance**

- [Users & CUJs](docs/prd/04-users-and-cujs.md) · [Feature Parity](docs/prd/10-feature-parity.md) · [Predecessor Gap Closure](docs/prd/24-predecessor-gap-closure.md) · [Decisions](docs/prd/11-decisions.md) · [Traceability](docs/prd/12-traceability.md)

**Operations**

- [Risks](docs/prd/08-risks.md) · [Non-Functional Requirements](docs/prd/13-non-functional-requirements.md) · [Pack Registry & Governance](docs/prd/17-pack-registry-and-governance.md) · [Roadmap](docs/prd/09-roadmap.md)

## Project

- [Contributing](https://github.com/agentsec-ecosystem/.github/blob/main/CONTRIBUTING.md) ·
  [Governance](https://github.com/agentsec-ecosystem/.github/blob/main/GOVERNANCE.md) ·
  [Code of Conduct](https://github.com/agentsec-ecosystem/.github/blob/main/CODE_OF_CONDUCT.md)
- [Security policy](SECURITY.md)
- [Roadmap](docs/prd/09-roadmap.md) · [Org roadmap](https://github.com/agentsec-ecosystem/.github/blob/main/ROADMAP.md)
- License: [Apache-2.0](LICENSE)

## License

Apache License 2.0 — see [LICENSE](LICENSE).
