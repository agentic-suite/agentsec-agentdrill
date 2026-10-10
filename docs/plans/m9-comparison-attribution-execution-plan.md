# agentdrill M9 — Golden Results, Comparison & Attribution Execution Plan

**Spec:** [WBS M9](../wbs/v0.1.0/wbs-v0.1.0-part5-determinism-comparison.md#milestone-m9--golden-results-comparison--attribution) ·
[design/comparison](../design/comparison.md).

## Constraints
Exit gate: suite green · coverage ≥95% · lint strict. **Golden-lock (DD-28):** flag, never silently fix.

## Tasks
- **T1 — Golden expected results (9.1):** preregistered, locked per pack version; undeclared change ⇒ flagged + re-pin note.
- **T2 — Comparison engine (9.2):** per-case / per-tag / aggregate deltas.
- **T3 — Change detection (9.3):** distinguish `adapter_changed` / `model_changed` / `oracle_changed` from a regression; `--allow-adapter-change`. *RED:* a swap is not a regression. *GREEN.*
- **T4 — Attribution (9.4, F38, CUJ-14):** correlate a blocked→missed flip with the config/pin/adapter diff; emit `attributed_to` + stage/mechanism + confidence; unattributable ⇒ `unknown` (never guessed).
- **T5 — Outcome classification (9.5):** `adapter_failed` / `agent_crashed` / `scenario_failed`.
- **T6 — Golden store (9.6):** `.agentdrill/goldens/` bound to `pack@version+hash`.
- **T7 — Tests + docs (9.T, 9.D).**

**Exit:** golden-lock enforced; adapter/model/oracle changes distinguished; flips attributed with mechanism or `unknown`. **Closure:** standard.
