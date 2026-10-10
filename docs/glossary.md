# Glossary

| Term | Meaning |
|---|---|
| **Attack pack** | Versioned replay of documented incident patterns (YAML). |
| **Case** | One attack step bound to a target + an oracle. |
| **Driver** | Adapter that delivers the attack (subprocess/python/http/harness). |
| **Target** | Adapter for a deployed-stack component; reads decisions + evidence. |
| **Oracle** | Decides `blocked` / `missed` / `degraded` (deterministic first, judge where needed). |
| **Outcome split** | The honest result label: blocked / missed / degraded. |
| **Efficacy** | The unguarded control group; a case counts only if it succeeds unguarded. |
| **`attack_inert`** | A case that fails even unguarded — excluded from enforcement rates. |
| **Utility-under-attack** | Benign utility while attacks are in play (the price of a block). |
| **`benign_twin`** | The benign counterpart of an attack case. |
| **Attestation** | `live` / `fixture` / `mock` — how real the target was; weakest link labels the run. |
| **Kill-chain** | attack_start → delivered → detected → decided → halted → revoked → **ceased**. |
| **`ceased`** | Cessation, established by **probe** (re-attempt the guarded action). |
| **`cease_gap`** | Revoked but still acting — the dashboard-green/damage-continues failure. |
| **Evidence** | agentwatch security events tied to a result. |
| **`telemetry_gap`** | `blocked` verdict with no corresponding agentwatch event. |
| **Golden-lock** | Preregistered expected results; changes flagged, never silent. |
| **Dark holdout** | Unpublished holdout subset that detects pack-gaming. |
| **Drill-the-drill** | Meta-verification: adversarial cases against agentdrill's own oracles. |
| **Evasion pack** | Self-attack pack against the ecosystem's own tools. |
| **Calibration corpus** | Labeled data measuring oracle agreement/false rates. |
| **Standalone verifier** | Offline, zero-install verification of a bundle/release. |
| **Run manifest** | Reproducibility manifest (pins, digests, env names). |
| **CART** | Continuous automated red teaming — trigger-driven re-drilling. |
| **Seam** | A gap *between* two controls (composition failure). |
| **fix_decay** | A shipped fix that silently stopped holding. |
| **agentwatch** | The ecosystem's record + security-event schema (consumed by agentdrill). |
