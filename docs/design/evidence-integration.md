# Evidence Integration — Design

**BLUF:** agentdrill emits and consumes the **agentwatch** record + security-event schema (DD-05) — one
schema, one source of truth. Every result is **evidence-bound**; a `blocked` verdict with no corresponding
event is a `telemetry_gap` (the *observability* of the defense, proven too).

> **Implemented (M7).** Code in `src/agentdrill/evidence/` (`schema`, `binding`, `telemetry`, `artifacts`,
> `coverage`); `Evidence` lives in `models/evidence.py`. Reference:
> [../reference/evidence-and-telemetry.md](../reference/evidence-and-telemetry.md).

## What we read

Security events from agentwatch: `denied`, `policy-fired`, `secret-detected`, `revoked`, `halted` — plus
the tool-call record. agentdrill does **not** redefine the schema; it imports/validates it.

## Binding rules

1. Every `Result` references the evidence behind it.
2. Missing evidence ⇒ an explicit **`evidence_gap`** finding (never a silent pass).
3. Each case may declare **`expect_telemetry`** — the events a true block must produce. A `blocked` verdict
   without them ⇒ **`telemetry_gap`** finding.
4. Evidence refs are written into `artifacts/<case_id>.json` so a result reconstructs its evidence.

## Coverage reconciliation

`agentdrill coverage` consumes the agentwatch **inventory** (tools, MCP servers, capabilities) and reports
exercised vs. unexercised surfaces; **`gap:unexplained` must be zero** — the same discipline agentwatch
uses for its own capture.

## Verifier seam

Evidence bundles are verifiable offline (F64) with **redaction receipts** (F65): the recipient sees *that*
something was redacted, not *what*. The verifier checks receipts against the redaction policy.

## Why this matters

Most red-team tools stop at "did the control block?" agentdrill also proves "did the control *say* so?" —
because a block with a broken evidence path leaves dashboards, alerts, and compliance blind to the next one.
