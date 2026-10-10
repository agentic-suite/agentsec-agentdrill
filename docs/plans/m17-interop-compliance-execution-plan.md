# agentdrill M17 — Interop, Standards Tagging & Compliance Execution Plan

**Spec:** [WBS M17](../wbs/v0.1.0/wbs-v0.1.0-part9-registry-interop.md#milestone-m17--interop-standards-tagging--compliance) · [PRD 03](../../prd/03-landscape.md).

## Constraints
Exit gate + gates. **Import, don't reinvent** (R9); every pack/attack tagged (R10, lint-enforced).

## Tasks
- **T1 — Interop importer (17.1, F12):** promptfoo/garak/AgentDojo/PyRIT → packs; format-translation only. *RED:* imported suite runs unchanged. *GREEN.*
- **T2 — Standards tagging (17.2, F13):** MITRE ATLAS + OWASP on every pack/attack; lint requires tags.
- **T3 — Adversary profiles (17.3, F54):** pack-level threat-intel card.
- **T4 — Compliance-mapped reporting (17.4, F24):** EU AI Act Art.12 / NIST AI RMF / ISO 42001; evidence export to agentcomply.
- **T5 — Standards submission + fuzzing (17.5, F28, R13):** NIST CAISI / AgentDojo-Inspect; OSS-Fuzz pack class.
- **T6 — Competitor benchmark (17.6, R12):** third-party rows via PR submission (F57).
- **T7 — Gates + docs (17.T/.C/.L/.CR/.D).**

**Exit:** suites import; tagging enforced; compliance + submission generate offline. **Closure:** standard.
