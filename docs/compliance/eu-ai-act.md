# EU AI Act Mapping (Art. 9 / 12 / 15)

The EU AI Act (Reg. (EU) 2024/1689) requires **risk management (Art. 9)**, **record-keeping (Art. 12)** and
**accuracy, robustness and cybersecurity (Art. 15)** for high-risk AI systems. agentdrill produces
continuously-verified evidence that these controls actually work. Built (v0.1.0).

> **Dates (post Digital Omnibus on AI, Reg. (EU) 2026/1744, in force 2026-07-27):** Annex III stand-alone
> high-risk obligations moved to **2027-12-02**; Annex I to **2028-08-02**; Art. 50 transparency largely
> unchanged (**2026-08-02**). Dates from secondary summaries — **confirm with counsel** before any statement
> ([PRD 42](../prd/42-standards-and-claims.md)).

## What agentdrill contributes

| Need | Article | agentdrill artifact |
|---|---|---|
| Risk-management evidence (tested controls) | Art. 9 | risk-driven drilling via the attack-path graph; CI gate |
| Logs conforming to a recognized standard | Art. 12 | results/evidence in the **agentwatch** schema; offline-verifiable evidence bundles |
| Accuracy / **robustness / cybersecurity** evidence | Art. 15 | efficacy-backed blocked/missed/degraded; attacker-strength pressure curves; kill-time; witness-confirmed effects |
| Change management evidence | — | CI gate rejecting un-blocking policy changes; fix-validation (`fix_decay`) |
| Continuous assurance | — | trigger-driven re-drills on config/model/policy change; per-release benchmark |
| Transparency (incl. misses) | — | limitations register; adjudication process with a resolution SLA |

Every release ships an **evidence index** per article with an explicit **what is not evidenced** column.

## Adjacent regimes

CRA / NIS2 / DORA (resilience testing + disclosure): our coordinated disclosure ([PRD 37](../prd/37-break-it-program.md))
and exposure ledger ([PRD 33](../prd/33-exposure-ledger-and-waivers.md)) supply relevant evidence. Date
claims for CRA reporting must be **verified** before use.

## Honesty

agentdrill **supports** Art. 12 evidence; it does not itself certify compliance. Evidence exports to
**agentcomply** for the compliance report, and every row cites a third-party-verifiable artifact
(`agentdrill verify`).
