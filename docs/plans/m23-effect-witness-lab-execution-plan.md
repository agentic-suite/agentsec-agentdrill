# agentdrill M23 — Effect Witness & Adversary Lab Execution Plan

**Spec:** [WBS M23](../wbs/v0.1.0/wbs-v0.1.0-part13-effect-witness-bypass.md) · [design](../design/effect-witness-and-lab.md) · [PRD 26](../prd/26-independent-effect-witness.md), [PRD 27](../prd/27-adversary-lab.md).

## Constraints
Non-circular oracle first: witnesses live **outside** the defended stack. Lab is loopback-only, seed-deterministic, documented-pattern-only, signed. Standard gates.

## Tasks
- **T1 — Effect declarations (23.1):** forbidden + preserved effects in the pack schema/loader. *RED:* case without effects is flagged. *GREEN.*
- **T2 — Witnesses (23.2–23.4):** FS canary, network sinkhole, honey credentials, process/syscall, side-effect ledger, human-surface. *RED:* planted effect seen when it happens (≤2 s median). *GREEN.*
- **T3 — Two-oracle verdict (23.5):** decision × witness → verdict set + `witness_discrepancy`/`blocked_silently`/`witness_unavailable`; hash-chained witness log; `witness: live|none` label.
- **T4 — Adversary Lab (23.6–23.8):** evil MCP server (+ rug-pull), test IdP/OAuth, hostile registries, rogue API, evil A2A peer, sinks; ≥12 content carriers; loopback + ground-truth log + `lab@version` pin. *RED:* same seed ⇒ same lab event log. *GREEN.*
- **T5 — Egress/interpolation guard:** zero non-loopback egress (network-capture test).
- **T6 — Gates + docs (23.T/.C/.L/.CR/.D).**

**Exit:** ≥90% enforcement cases witnessed; discrepancy detection ≥99% on seeded faults; lab determinism ≥99.9%; zero egress. **Closure:** standard.
