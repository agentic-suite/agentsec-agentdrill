# agentdrill M29 — Detonation, Break-It & Frontier Attack Classes Execution Plan

**Spec:** [WBS M29](../wbs/v0.1.0/wbs-v0.1.0-part16-frontier-platform-standards.md) · [design](../design/detonation-breakit-frontier.md) · [PRD 36](../prd/36-extension-detonation-lab.md), [PRD 37](../prd/37-break-it-program.md), [PRD 39](../prd/39-frontier-attack-classes.md).

**Status:** 🚧 In progress (2026-10-24) · **Issues:** #359–#370 · Closes gaps **G12, G13, G15**.

## Constraints

- Detonation runs in **strict isolation**, RoE-governed, **no real egress**; a clean report is **bounded
  evidence, never "safe"**; the report states conditions covered / not covered.
- Documented patterns only; rogue/self-modification framed as **oversight subversion**, never capability uplift.
- Break-It accepted payloads stay **private until fix + embargo**; published artifacts are family-level.
- Every frontier class ships with benign twins + witness effects + cleanup, and needs **dual-use sign-off**.
- One ticket at a time: test **RED** → implement **GREEN** → next. Full suite at milestone end only.

## Prerequisites

- Consumes **M23** (`lab/`, `witness/` — the isolated lab, canaries, sensors), **M24** (route families,
  `promote_to_regression` via M18 F61), **M13** (`efficacy/`), **M28** (`roe/` — detonation is RoE-governed),
  **M2/M14** (pack schema, benign twins), **M17** (`interop/tagging` — ASI/ATLAS).

## Tasks

- **T1 — Detonation lab (29.1, #359).** Run MCP servers/skills/plugins/hooks/rules/packages in the hermetic
  lab; observe egress / honey-reads / out-of-scope writes / spawn / metadata drift / conditional behaviour /
  declared-vs-actual; `BehaviorReport` + prior-version diff + honesty labels. *RED:* seeded recall ≥80 %, zero
  escapes. *GREEN.*
- **T2 — Break-It program (29.2, #360).** Pinned reference configs; structured proof-of-bypass **auto-verified
  by the witness**; triage SLA + severity; coordinated disclosure (fix window, embargo, CVE/CWE); accepted
  bypass → regression + family catalogue. *RED:* ≥80 % auto-verified, ack ≤24 h. *GREEN.*
- **T3 — Corpus import (29.3, #361).** Import public human-found corpora (licence check) into packs/catalogue.
- **T4–T7 — Frontier classes (29.4–29.7, #362–#365).** Class 4 identity/OAuth; 1 approval abuse + 5 memory &
  persistence; 7 denial-of-wallet + 6 multi-agent cascade; 2 browser + 3 multimodal + 8 AP2 (spec-gated stub).
  Each: a pack-class descriptor, benign twins, witness effects, cleanup, and the class's acceptance check.
- **T8 — Gates + docs (29.T #366 · 29.C #367 · 29.L #368 · 29.CR #369 · 29.D #370).** tests; coverage ≥95 %;
  `ruff` + `mypy --strict`; review log; detonation profiles + disclosure policy + per-class pack docs.

## Module ownership (single-writer files)

- New packages `agentdrill/detonation/` (29.1), `agentdrill/breakit/` (29.2–29.3), `agentdrill/frontier/`
  (29.4–29.7) — proposed.
- **Reuse, do not fork:** `lab/` (isolation), `witness/` (evidence), `roe/` (governance), `efficacy/`,
  `interop/tagging` (ASI/ATLAS), `ledger`/`attestations` (registry admission artifact).
- The **frontier class registry** and the **ASI coverage count** are single-writer here.

## Exit criteria

- [ ] All tests pass · coverage ≥95 % · `ruff` zero · `mypy --strict` clean · docs linked.
- [ ] Detonation recall ≥80 %, **zero lab escapes**; Break-It pilot converts accepted bypasses.
- [ ] ≥6/10 ASI categories efficacy-verified + witnessed (v0.2 → ≥9/10).
- [ ] Dual-use review sign-off per class (recorded); AP2 marked **spec-gated**.

**Closure:** standard (implemented · gates run once · committed · pushed · issue closed · docs updated · checkpoint).
