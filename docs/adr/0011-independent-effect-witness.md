# ADR-0011 — Independent effect witness is a primary oracle input

- **Status:** proposed (2026-10-10)
- **Context:** Oracles currently decide `blocked/missed/degraded` largely from the defense's own evidence
  (agentwatch events, expected telemetry). This is circular: a defense can log `denied` while a side effect
  still lands, and stealth attacks (agent reports success while compromised) are invisible. Best-in-class
  agent benchmarks grade **environment state**, not text.
- **Decision:** Enforcement cases declare **forbidden/preserved effects**; **witnesses outside the defended
  stack** (canary FS, network sinkhole, honey credentials, process/syscall, side-effect ledger, human
  surface) confirm whether they occurred. The defense's verdict and the witness are compared; a
  `blocked` claim without witness confirmation is labeled; disagreement (`witness_discrepancy`) is a
  first-class finding ([PRD 26](../prd/26-independent-effect-witness.md)).
- **Consequences:** stronger, non-circular evidence; a new witness subsystem and its integrity controls;
  canary-only invariant required (see ADR-0012); witness coverage becomes a published metric; some results
  are correctly downgraded to `witness: none` where no witness exists.
