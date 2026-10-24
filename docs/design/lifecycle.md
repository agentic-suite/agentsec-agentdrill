# Lifecycle — Intake, Fix-Validation, Seams, Attestation, Verifier, Quickstart — Design

**BLUF:** The features that keep the benchmark honest and fresh — a 7-day intake SLA, fix-decay
detection, **seam** probing, target **attestation**, a zero-install **verifier**, **evidence privacy**
(receipts), a ≤15-minute **quickstart**, the MCP/memory pack classes and the closes-the-loop policy
suggestion.

> **Status:** normative (M18). **Implementation:** `agentdrill/lifecycle/` — `intake.py` (F60),
> `fix_validation.py` (F61), `seams.py` (F62), `attestation.py` (F63), `verifier.py` (F64),
> `privacy.py` (F65), `quickstart.py` (F66), and the MCP/memory packs (F19/F20), plus
> `policy_suggestion.py` (F21). Reference: [lifecycle](../reference/lifecycle.md). Spec:
> [PRD 20](../prd/20-efficacy-freshness-lifecycle.md).

## Intake + fix-validation (18.1/18.2, F60/F61)

A watchlist incident is assessed **≤7 days** — a pack draft or an explicit **N/A with a reason**
(`assess`, `SLA_DAYS`). Every fixed miss becomes a **permanent pinned regression case**
(`regression_case`); a fix that stops holding is `fix_decay` — **release-blocking** with attribution
(`require_fix_holds`).

## Seams + attestation (18.3/18.4, F62/F63)

`probe_seam` finds a composition gap (denied-then-retried) and names **both controls** (`seam_gap`).
A result is labeled at its **weakest link** (`live`/`fixture`/`mock`); a `mock` result **never
publishes** (`require_publishable`).

## Verifier + privacy (18.5/18.6, F64/F65)

`verify_bundle` verifies a bundle **offline** with three verdicts — `intact` (signatures + hashes),
`complete` (manifest + labels), `honest_shaped` (≥3 seeds, non-empty split, no composite score).
`redact` redacts **before bundling** with **receipts** (class, count, location); `verify_receipts`
checks them.

## Quickstart + pack classes (18.7/18.8, F66/F19/F20)

`agentdrill quickstart` boots a bundled demo and reaches a first honest result in **≤15 minutes** —
mock-attested and watermarked `demo — never evidence`. New pack classes: MCP tool surface
(poisoning / rug-pull / shadowing / WhatsApp-class) and memory/multi-agent abuse.

## Closes-the-loop (18.9, F21)

A confirmed miss emits an **advisory** rule + a what-if replay proving it closes the miss; the fix is
proposed as a **reviewed PR** and is **never auto-applied**.
