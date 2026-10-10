# agentdrill v0.1.0 — Architecture Specification

**Status:** draft (design intent). A concise architecture of the shipped system; rewritten against the
built code at M31–M32.

## Overview

agentdrill is a Python core with a CLI wrapper and a pytest-style API (ADR-0001). All three share one
runner, oracle engine, and adapter surface.

```
agentdrill (CLI) ─┐
agentdrill (pytest)─┼─→ Runner ─→ Driver ─→ harness/agent ─→ deployed stack (targets)
agentdrill (lib) ─┘        │                                         │
                           ├─ Oracle (deterministic | judge | hybrid) │
                           ├─ Evidence (agentwatch schema) ←──────────┘
                           ├─ Efficacy (unguarded twin) · Kill-chain (probe)
                           └─ Reporter / Benchmark · CI gate
```

## Surfaces

| Surface | Entry | Use |
|---|---|---|
| Library | `from agentdrill import runner` | programmatic, notebooks, host test suites |
| CLI | `agentdrill run --pack …` | local dev, CI |
| pytest | `agentdrill test run …` | team workflows, gating |

## Contracts

- **Pack format** — [../reference/pack-format-spec.md](../reference/pack-format-spec.md) (normative).
- **Adapter** — [../reference/adapter-api.md](../reference/adapter-api.md).
- **Evidence** — the agentwatch record + security-event schema (external).
- **Run artifacts** — `.agentdrill/runs/<id>/` ([storage-design](../design/storage-design.md)).

## Principles

1. **Observe, don't enforce** (ADR-0003).
2. **No ground-truth leakage** (ADR-0005).
3. **Deterministic first** (ADR-0006); divergences flagged.
4. **Efficacy-backed** (ADR-0007); **kill-time = cessation** (ADR-0008).
5. **Honest by construction** — misses mandatory, multi-seed, signed, verifiable.
