# agentdrill — User Guide

> **Prove what your agent defenses actually stop.** Attack packs run in CI against your *deployed* stack,
> with honest, published results — the misses included.

**Status:** built (v0.1.0). Commands are stable.

---

## The question agentdrill answers

*"Does my deployed agent-security config actually stop the attacks that already happened — and can I prove
it?"* A demo, a vendor claim, or a one-off red-team report can't. A versioned pack, run against your exact
stack, with a reproducible result, can.

## Table of contents

| # | Section |
|---|---|
| 1 | [Core concepts](#1-core-concepts) |
| 2 | [Your first drill](#2-your-first-drill) |
| 3 | [Writing packs](#3-writing-packs) |
| 4 | [Running & reading results](#4-running--reading-results) |
| 5 | [Kill-time](#5-kill-time) |
| 6 | [Efficacy & utility](#6-efficacy--utility) |
| 7 | [CI gating](#7-ci-gating) |
| 8 | [The public benchmark](#8-the-public-benchmark) |
| 9 | [Gotchas](#9-gotchas) |

## 1. Core concepts

- **Attack pack** — a versioned replay of documented incidents.
- **Case** — one attack step bound to a target + an oracle.
- **Driver / Target** — deliver the attack / are the deployed enforcement path.
- **Oracle** — decides `blocked` / `missed` / `degraded` (deterministic first).
- **Efficacy** — the unguarded control group; **kill-time** — cessation, probed.

## 2. Your first drill

```sh
# Install (PyPI) — first release: v0.1.0
pip install agentsec-agentdrill==0.1.0
# Verify the download (optional): compare the wheel hash with the release SHA256SUMS;
# SBOM + provenance: docs/release/v0.1.0/release-evidence.md
agentdrill quickstart                       # bundled demo, ≤15 min, honesty-shaped
agentdrill run --pack incidents-core --target ./stack.yaml --sandbox
```

## 3. Writing packs

`agentdrill init --template <class>` → edit → `agentdrill pack lint` → `agentdrill validate --strict`.
Every case needs an `incident_ref`, oracle, benign twin (for enforcement), cleanup (if stateful), and
ATLAS/OWASP tags. See [tutorial 02](../tutorials/02-write-an-attack-pack.md).

## 4. Running & reading results

```sh
agentdrill run --pack incidents-core --target ./stack.yaml --tags destructive-command
agentdrill run --pack incidents-core --target ./stack.yaml --dry-run --explain   # plan, no execution
```

Results are `blocked` / `missed` / `degraded` with dimensions
(`compatibility`/`enforcement`/`integrity`), evidence refs, and an exit code. **Misses are always present.**

## 5. Kill-time

```sh
agentdrill run --pack kill-chain --target ./stack.yaml --tags kill-time
```

A stage timeline ending at a **probed** `ceased`; per-stage p50/p95/max; `cease_gap` = revoked but still
acting. See [tutorial 04](../tutorials/04-verify-kill-time.md).

## 6. Efficacy & utility

Every enforcement number is backed by an unguarded success (else `attack_inert`, excluded). Every block
carries its **utility price tag** (benign utility + utility-under-attack).

## 7. CI gating

```sh
agentdrill run --pack incidents-core --target ./stack.yaml --ci --fail-on enforcement
```

Exit 1 on a miss, 4 on a critical enforcement miss. See [runbook](../runbooks/gate-a-policy-pr.md).

## 8. The public benchmark

Per release: honest outcome split, kill-time, coverage heat-map, trend, traces-per-row, limitations
register. Reproduce it in [tutorial 05](../tutorials/05-verify-a-release.md).

## 9. Gotchas

- **`mock` never publishes** — a `mock`-attested result is an authoring aid, not evidence.
- **A green with no misses** is suspicious, not impressive.
- **Inert attacks don't count** — if it can't land unguarded, it isn't coverage.
- **A fix isn't done when it ships** — it's done when it holds (`fix_decay`).
- **Single-run numbers aren't claims** — ≥3 seeds, or it fails the publish check.

---

**Where to go next:** [design](../design/README.md) · [reference](../reference/README.md) ·
[runbooks](../runbooks/README.md) · [PRD](../prd/README.md).
