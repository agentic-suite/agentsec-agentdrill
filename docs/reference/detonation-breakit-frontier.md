# Detonation, Break-It & Frontier Attack Classes — Reference

**BLUF:** Detonate unknown extensions in the hermetic lab, invite a crowd to break a pinned reference range,
and ship the attack classes that close the OWASP **ASI** gaps. **Normative (M29).** Packages:
`agentdrill/detonation/`, `agentdrill/breakit/`, `agentdrill/frontier/`. Source design:
[design/detonation-breakit-frontier.md](../design/detonation-breakit-frontier.md); PRD
[36](../prd/36-extension-detonation-lab.md) (R72), [37](../prd/37-break-it-program.md) (R73),
[39](../prd/39-frontier-attack-classes.md) (R75). Closes gaps G12, G13, G15.

## Extension detonation (`agentdrill/detonation/`)

`run_detonation(spec, events=…)` → `BehaviorReport`. Detects **9 behaviours**: egress, DNS, honey-read,
out-of-scope write, process spawn, metadata drift, conditional behaviour, declared-vs-actual, injection
content — each with evidence, ATLAS tags and a suggested policy.

- The report is **bounded evidence**: it always lists `conditions_not_covered`, and a clean report is
  **never "safe"** (`bounded_evidence=True`).
- `prior_version_diff` flags a **rug pull** (new behaviours vs. the prior version).
- Gates: **seeded recall ≥ 80 %** (`require_recall`) and **zero escapes** (`require_no_escapes`); the
  lab is RoE-governed and has no real egress.
- Evasion awareness: multi-schedule runs (time-shifted, repeated, varied personas) reported as coverage.

## Break-It program (`agentdrill/breakit/`)

Pinned reference range → structured proof-of-bypass → **auto-verified by the M23 witness** (never the
reporter's word) → triage with a **24 h ack SLA** + severity → **coordinated disclosure** (30–90 d fix
window, embargo ≥ window, CVE/CWE, credit) → **accepted bypass → a permanent regression** (F61, reusing
M24/M18) + the route-**family** catalogue. **Auto-verified rate gate ≥ 80 %**. Accepted payloads stay private
until fix + embargo; published artifacts are family-level.

**Corpus import:** `import_corpus` maps a public human-found corpus (e.g. ART) into a pack — **licence-checked**
(OSS/CC allow-list) and **lint-clean** (ATLAS + OWASP per case, via M17's tagging SSOT).

## Frontier attack classes (`agentdrill/frontier/`)

`FRONTIER_CLASSES` — each a pack class with twins, witness effects and cleanup; a class is useful only once
its ASI category is **efficacy-verified and witnessed** (`asi_coverage`, gate ≥ 6/10 at v0.1.0 → ≥ 9/10 at
v0.2).

| # | Class | ASI | Acceptance check |
|---|---|---|---|
| 1 | HITL / approval abuse | ASI09 | `approval_fidelity` (step-up + rendered diff), default 100 % |
| 2 | Computer-use / browser | ASI01/02/05 | `require_browser_guards` (sandbox + allowlist + form-fill) |
| 3 | Multimodal injection | ASI01 | `require_carriers` (**≥ 12 carriers**) |
| 4 | Identity, delegation & OAuth | ASI03 | `require_audience_rejection` (100 %) |
| 5 | Memory & persistence | ASI06 | `require_no_persistence` (**persistence 0**) |
| 6 | Multi-agent cascade & rogue agents | ASI07/08/10 | `require_bounded_handoff` (**≤ 1 hop**) |
| 7 | Resource exhaustion / denial-of-wallet | LLM10 | `require_cost_within_ceiling` (**≤ +5 %**) |
| 8 | AP2 payments (**spec-gated stub**) | ASI03 | `require_spec_gated` (never over-claimed) |

Every class needs a **dual-use review sign-off** (`require_dual_use_signed`). Documented patterns only;
rogue/self-modification is framed as **oversight subversion**, never capability uplift.

## Known limitations

- The classes ship as **class descriptors + acceptance checkers**; the runnable pack cases execute against
  the deployed stack in the M31 field tests.
- Detonation detection operates over the lab's observed event stream (real events at M31).
- The Break-It range hosting, rewards and CNA submission are program operations.
