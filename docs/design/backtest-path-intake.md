# Backtest, Attack-Path Graph & Incident Intake — Design

**BLUF:** Turn real history and inventory into **risk-driven** drilling: backtest a candidate policy against
recorded sessions (with a false-block budget), build a capability/attack-path graph from inventory and drill
by **reachable harm**, and compile fresh advisories into reviewed packs fast. WBS
[M27](../wbs/v0.1.0/wbs-v0.1.0-part15-context-governance.md). Reference:
[PRD 30](../prd/30-trace-backtest-and-shadow.md), [PRD 31](../prd/31-attack-path-and-blast-radius.md),
[PRD 32](../prd/32-incident-to-pack-compiler.md).

> **Design intent** (pre-build). Rewritten against the built system at M31–M32.

## Trace backtest & shadow (F92)

- **Backtest:** replay redacted agentwatch sessions against a candidate policy offline → newly blocked
  benign clusters, regressions, unchanged, **un-replayable itemized** (never ignored). Replay fidelity ≥99%.
- **Shadow mode:** candidate runs **log-only** beside the enforced one; divergence rate + clusters;
  provably side-effect-free (M23 witness).
- **False-block budget:** policy declares a budget (e.g., ≤0.5% of benign calls / trailing 30 d); backtest
  measures it with a CI; over-budget fails the gate with clusters.
- **Trace → drill:** promote a session → redacted case + mined benign twins (`origin: production-trace`, HITL).

## Attack-path graph (F93)

```
nodes: agents, tools, mcp_servers, credentials/scopes, data_sources, egress_routes,
       memory_stores, sub_agents, approval_settings, instruction_files
structural_findings: trifecta_present, over_scoped_token, unrestricted_egress,
       auto_approve_plus_shell, writable_instruction_file, shared_memory, identity_inheritance
paths: untrusted_input → … → crown_jewel/effect
path_status: proven_broken | open_missed | unproven | accepted
```

Per-path **AIVSS-compatible severity** (never aggregated). Each critical path **binds** the cases that should
prove it broken (feeds diff-aware selection F76). A config change that opens a **new path** triggers a drill.
Blind spots render as `unknown nodes`; static reachability ≠ exploitability → status needs **drill proof**.

## Incident-to-pack compiler (F94)

```
intake feeds (GHSA/CVE, ATLAS, incident DBs, vendor advisories, arXiv) → dedup
  → relevance filter vs. inventory
  → cite-or-drop incident brief        # uncited facts dropped
  → draft pack from lab generators (F88) + twin + cleanup + witness effects + preregistered outcome
  → efficacy check (F59) → dual-use screen → HITL review (reviewer ≠ drafter) → registry (F39)
```

Intake content is **untrusted** → it runs in the lab with no tools/secrets. Drafting model is pinned in the
manifest; LLM is a tool, not authority.

## Invariants

1. Backtest/shadow disclose fidelity; shadow is side-effect-free.
2. Trace-derived cases are redacted (receipts verified); zero unredacted secrets.
3. Cited-or-dropped; no payload invention beyond the source.
4. Reachability is a hypothesis until a drill proves the path.

## Open questions
1. Minimum trace schema from third-party harnesses (OTel GenAI spans may suffice).
2. Graph persistence (ephemeral + snapshot hash vs. long-lived store).
3. Publish incident briefs publicly (STIX)?
