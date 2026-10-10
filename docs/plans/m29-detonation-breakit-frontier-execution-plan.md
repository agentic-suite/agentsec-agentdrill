# agentdrill M29 — Detonation, Break-It & Frontier Classes Execution Plan

**Spec:** [WBS M29](../wbs/v0.1.0/wbs-v0.1.0-part16-frontier-platform-standards.md) · [design](../design/detonation-breakit-frontier.md) · [PRD 36](../prd/36-extension-detonation-lab.md), [PRD 37](../prd/37-break-it-program.md), [PRD 39](../prd/39-frontier-attack-classes.md).

## Constraints
Strict isolation (VM/microVM), no real egress. Documented patterns only. Dual-use review per class. Break-It payloads private until fix + embargo.

## Tasks
- **T1 — Detonation lab (29.1):** run extensions in the lab; observe via M23 witnesses; Behavior Report + version diff + honesty labels. *RED:* seeded recall ≥80%, zero escapes. *GREEN.*
- **T2 — Break-It program (29.2):** reference ranges; witness auto-verify; triage SLA + severity + family dedup; coordinated disclosure; convert to regression. *RED:* ≥80% auto-verified, ack ≤24 h. *GREEN.*
- **T3 — Corpus import (29.3):** ART-class corpora → lint-clean packs.
- **T4 — Frontier classes (29.4–29.7):** identity/OAuth · approval+memory · wallet+cascade · browser+multimodal (+AP2 stub); each with twins + witnesses + cleanup. *RED:* per-class efficacy verified. *GREEN.*
- **T5 — Gates + docs (29.T/.C/.L/.CR/.D).**

**Exit:** detonation recall ≥80%, zero escapes; ≥6/10 ASI categories efficacy-verified + witnessed; dual-use sign-off. **Closure:** standard.
