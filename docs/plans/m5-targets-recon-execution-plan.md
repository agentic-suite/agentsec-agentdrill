# agentdrill M5 — Target Adapters & Recon Execution Plan

**Spec:** [WBS M5](../wbs/v0.1.0/wbs-v0.1.0-part3-drivers-targets.md#milestone-m5--target-adapters--reconscoping) ·
[design/data-dictionary](../design/data-dictionary.md) · [PRD 02](../../prd/02-architecture.md).

## Global constraints

- Exit gate: suite green · coverage ≥95% · lint strict clean.
- **Surface honesty:** a case bound to a nonexistent surface fails **loudly**, never silently passes.
- Targets own the deployed enforcement path — agentdrill still owns **no** enforcement (ADR-0003).

## Tasks

### T1 — Target adapter base (5.1)
`Target` ABC: `drive(case)`, `read_decision()`, `read_evidence()`, `attestation`. Contract documented.

### T2 — Deployed-stack targets (5.2)
`agentgate`, `agentkeys`, `agentseatbelt`, `agentkernel`, `policyweave-output`, `agenthalt`. **RED** → per-target
drive/decision/evidence tests → **GREEN**.

### T3 — Recon/scoping (5.3)
Probe exposed surface (tools/MCP servers/capabilities via agentwatch inventory) → `ReconSnapshot`; bind cases.
**RED** → missing-surface failure test → **GREEN**.

### T4 — Target config + attestation hooks (5.4)
Per-component config; `live`/`fixture`/`mock` recorded (enforced at M13/M18); weakest-link label computable.

### T5 — Model-surface sanity (5.5)
Declare `model`/`base_url`; recon fails loudly on an unreachable model surface before cases run (closes G12).

### T6 — `.agentdrill/` run layout (5.6)
Target metadata + recon ref stored with each run.

### T7 — Tests + docs (5.T, 5.D).

**Exit:** packs exercise the real enforcement path (R2); recon binds cases + fails on absent surfaces;
unreachable model surfaces fail before any case runs. **Closure:** standard.
