# agentdrill M8 — Determinism Execution Plan

**Spec:** [WBS M8](../wbs/v0.1.0/wbs-v0.1.0-part5-determinism-comparison.md#milestone-m8--determinism--fixtures-manifest--pins) ·
[design/storage-design](../design/storage-design.md).

## Constraints
Exit gate: suite green · coverage ≥95% · lint strict. Same environment ⇒ same result (R6); a changed pin is declared, never silent.

## Tasks
- **T1 — Fixtures/ToolStub (8.1):** record/replay target+tool responses; `--live` mutually exclusive. *RED:* two identical fixture runs ⇒ identical scores. *GREEN.*
- **T2 — Run manifest (8.2):** `run-manifest.json` (OS/arch/runtime/deps, target+driver digests, pack hash, oracle versions, env names only); `--no-manifest`.
- **T3 — Pins (8.3):** pin seeds/models/pack-hash/oracle versions; re-pin ⇒ re-publish rule wired.
- **T4 — Contamination checks (8.4, F30):** probe each case vs judge/target-model training posture; contaminated ⇒ flagged, never hidden.
- **T5 — Reproducibility test (8.5):** rerun a pinned pack ⇒ identical result unless a pin changed (declared).
- **T6 — Methodology doc (8.6):** publish how each oracle decides blocked/missed/degraded.
- **T7 — Tests + docs (8.T, 8.D).**

**Exit:** same env ⇒ same result; manifest complete; contamination flagged. **Closure:** standard.
