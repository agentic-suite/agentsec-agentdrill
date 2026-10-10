# Reporting & Benchmark — Design

**BLUF:** The honest reporter and the public benchmark: JSON / Markdown / GitHub-Actions / self-contained
HTML / PDF; every number **efficacy-backed, multi-seed, CI'd, trace-linked**; misses first-class; a
per-release **coverage heat-map** and **trend store**.

> **Design intent** (pre-build). WBS M10. Success metrics: [PRD 07](../prd/07-success-metrics.md).

## Formats

| Format | Use |
|---|---|
| JSON | machine consumption |
| Markdown | PR comments |
| GitHub-Actions | workflow annotations |
| HTML (self-contained) | offline, exec-shareable (no server, no network) |
| PDF | compliance consumers (agentcomply may re-render) |

## Honesty rules (enforced, not aspirational)

- **Misses mandatory** — a run cannot publish without its misses (R5, DD-06).
- **Multi-seed** — mean ± std over ≥3 pinned seeds; a single-run number fails the publish check (F29, DD-27).
- **CIs** — bootstrap confidence intervals on outcome rates (F55); bare percentages rejected.
- **Contamination disclosed** — flagged cases stay visible (F30, DD-30).
- **No composite "security score"** — the outcome split + misses, never an average that hides one.

## Published artifacts

| Artifact | Content |
|---|---|
| Outcome table | blocked / missed / degraded per pack, with severity + efficacy + attestation |
| Kill-chain table | per-stage p50/p95/max + typed findings |
| Utility column | benign utility / utility-under-attack / enforcement rate per enforced case |
| Coverage heat-map (F53) | pack/tag × control (`blocked/partial/missed/untested`) + delta |
| Trend store (F23) | per-defense-class deltas across releases |
| Trace links (F56) | every cell → full trajectory + evidence, one hop |
| Limitations register (F34) | the honest "what this does NOT test" per release |

## Submission

`agentdrill benchmark export` produces the pinned set + manifest + traces for fork→run→PR submissions
(F57) — the R12 enabler: the benchmark is reproducible enough that anyone can submit, no vendor consent needed.
