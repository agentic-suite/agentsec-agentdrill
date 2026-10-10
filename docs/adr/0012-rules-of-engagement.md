# ADR-0012 — Rules of engagement are mandatory; destructive effects are canary-only

- **Status:** proposed (2026-10-10)
- **Context:** agentdrill makes agents attempt destructive and exfiltrating actions against real deployed
  stacks. A mis-scoped run is a reportable incident (real data deleted, a third party hit, a tenant hammered).
  Existing safeguards (sandbox for untrusted packs, cleanup) protect *us from packs*, not the *target and
  bystanders from us*. Enterprise/legal buyers require authorization and abort.
- **Decision:** Any **non-demo** run requires a signed **Rules-of-Engagement** file (authorized targets +
  ownership proof, environment class, allowed effect classes, canary-only data limit, windows, rate/cost
  ceilings, blast-radius caps, tier ceiling, approvers, contacts, abort conditions). Preflight is
  **fail-closed**. Hard invariants: destructive/exfil effects target **canaries/ephemeral clones only**; no
  third-party infrastructure; `prod` is default-deny with two-person approval; a **global abort independent
  of the system under test**; verified teardown; per-action scope receipts
  ([PRD 35](../prd/35-rules-of-engagement-and-safe-fire.md)).
- **Consequences:** safe-by-construction firing; some friction offset by templates and a `local-demo` fast
  path; mitigates the dual-use risk (a tool with authorization + audit ≠ an arsenal); ownership-verification
  methods become a maintained contract.
