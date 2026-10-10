# NIST AI RMF Mapping

agentdrill's results map to the NIST AI RMF functions + Generative AI Profile. Design intent.

| Function | How agentdrill serves it |
|---|---|
| **Govern** | Published methodology, signed artifacts, adjudication process, limitations register |
| **Map** | Pack catalog + coverage heat-map (ATLAS/OWASP tactics × controls) |
| **Measure** | Efficacy-backed, multi-seed results with CIs; kill-time; utility-under-attack |
| **Manage** | CI gate rejects an un-blocking policy change; fix-validation catches decay; advisory policy loop |

## Risk-tier alignment

Agent systems with **real side effects and data boundaries** (the tier agentdrill serves) get continuous,
reproducible evidence of control effectiveness — the RMF's "measure" and "manage" in one loop.

## Evidence index (per release)

Every release ships an **evidence index**: `RMF function/subcategory → drills that provide evidence → date →
config digest → outcome → what is NOT evidenced`. The last column is mandatory
([PRD 42](../prd/42-standards-and-claims.md)).

## Methodology alignment (CAISI/AISI)

Results follow the NIST CAISI / UK AISI findings on agent-hijacking evaluation: **evaluations must be
adaptive** (attacker-strength tiers, [PRD 25](../prd/25-attacker-strength-and-pressure.md)) and **tested on
multiple attempts** (`Hold@k`/`ASR@k`). Environment-state grading is supplied by the independent effect
witness ([PRD 26](../prd/26-independent-effect-witness.md)); evaluation-gaming is countered by
drill-the-drill (F43).

## Related government sources

NIST AI 100-2 (agent additions — **verify**), NIST SP 800-53 + **COSAIS** control overlays (agent use
cases; in development), NIST SP 800-218A, CISA/NSA AI deployment guidance, NIST SP 800-61/800-115 (RoE/report
structure, [PRD 35](../prd/35-rules-of-engagement-and-safe-fire.md)).

## Caveat (honesty)

agentdrill provides **technical evidence** (what a control stops against a documented attack). It does not
attest organizational governance; that is agentcomply's scope. We publish the technical record it consumes,
and every index states what is **not** evidenced.
