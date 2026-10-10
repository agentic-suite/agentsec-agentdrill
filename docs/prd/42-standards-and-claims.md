# PRD 42 — Standards, Claims & Interop

**BLUF:** Security buyers and auditors punish vague standards claims. Adopt a **claim vocabulary** — **Conforms to** (normative spec, tested) · **Maps to** (tags + published coverage incl. gaps) · **Interoperates with** (round-trip tested) · **Aligned with** (informative) · ban "compliant/certified/secure" via a **claims linter** — a **master standards table**, **version pins + drift watcher**, and **standards participation**. Correct the PRD's draft-era citations to the final **OWASP Top 10 for Agentic Applications 2026 (ASI01–ASI10)**, current **AIVSS**, and current **ATLAS**.

**Status:** Draft — v0.1.0 addition (2026-10-10) · **Owner:** @deghosal-2026 · **Parent:** agentsec-ecosystem #209 · **Features:** F104 · **Reqs:** R78

## Why

- "OWASP-compliant" is not a real certification for a testing tool; several frameworks are drafts.
- PRD 05 still cites "OWASP Agentic drafts"; the ASI list is final (2025-12-09), AIVSS is at v0.8, ATLAS added agent techniques (v5.4.0, Feb 2026), and EU dates moved (Digital Omnibus).
- Version pins and a claims linter prevent over-claim and stale tags.

## Requirements (v0.1.0)

| # | Requirement | Acceptance criterion |
|---|---|---|
| **R78** | Enforce a **claim vocabulary** (linter over docs/release notes/UI), maintain a **master standards table** with **version pins**, and run a **standards drift watcher**. | 0 claims-linter violations at release; 100% of applicable cases carry ≥1 valid ASI + ATLAS tag; tag drift 0 at release; version lag ≤ 30 days. |

## Features

| # | Feature | Req | Notes |
|---|---|---|---|
| **F104** | **Standards, claims & interop**: claim vocabulary + **claims linter**; master table (OWASP ASI 2026 · OWASP LLM 2025 · OWASP AIVSS · OWASP AI Testing Guide · MITRE ATLAS/ATT&CK/D3FEND · NIST AI RMF/AI 100-2/SP 800-53+COSAIS/SP 800-115 · NIST CAISI + UK AISI Inspect + IETF BMWG draft · ISO/IEC 42001/27001/23894/29147/30111 · EU AI Act post-Omnibus · CSA AICM/MAESTRO · AIUC-1 · SARIF/OTel/OCSF/STIX/OSCAL/in-toto/SLSA/Sigstore/CycloneDX/VEX/CVSS/AIVSS/SSVC); version pins + drift watcher; ASI coverage + **ATLAS-mitigation** mapping; **evidence index** per framework with explicit `not covered`; standards participation (submit to OWASP ASI, ATLAS, CAISI, IETF BMWG, OTel SIG) | R78 | Consumes [PRD 34](34-drill-attestations-and-deploy-gate.md)/[PRD 38](38-security-ecosystem-integrations.md); OWASP ASI coverage in [PRD 39](39-frontier-attack-classes.md) |

### Claim discipline
- "produces **evidence relevant to** EU AI Act Art. 9/12/15" — never "satisfies."
- No single AIVSS roll-up score; per-finding CVSS v4.0 + AIVSS vector only.
- **ATLAS mitigation** mapping (not only attack techniques) → heat-map "which mitigations are proven vs. untested."

## CUJs

### CUJ-62 — Auditor evidence index
Show the evidence index for ISO/IEC 42001 Annex A and EU AI Act Art. 15 from a release: per-clause evidence + **what is not evidenced**. **Success:** 100% of indexes list non-coverage.

### CUJ-63 — Contributor tag lint
A case with ASI tag `ASI11` is rejected; deprecated ATLAS IDs flagged. **Success:** lint blocks invalid tags.

## Success metrics

| Metric | Target |
|---|---|
| Claims-linter violations in released docs/notes/UI | **0** |
| Applicable cases with valid ASI + ATLAS tags | ≥ 98% |
| Tag drift (invalid/deprecated IDs) at release | 0 |
| Standards-version lag (new version → pins updated) | ≤ 30 days |
| Conformance suites green (SARIF/OSCAL/in-toto/CycloneDX) | 100% in CI |
| Evidence indexes with explicit `not covered` | 100% |
| ASI categories covered (see [PRD 39](39-frontier-attack-classes.md)) | ≥ 9/10 by v0.2 |
| External standards contributions submitted/accepted | ≥ 1/year accepted; ≥ 1/release in review |

## Standards detail

### Claim vocabulary (mandatory in docs, UI, release notes)
| Verb | Meaning | Proof required | Example |
|---|---|---|---|
| **Conforms to** | We implement a normative spec; automated conformance tests pass | schema/validator in CI, published results | SARIF 2.1.0 output validates |
| **Maps to** | Items tagged with the standard's IDs; coverage **and gaps** published | tag-lint in CI; coverage table incl. `untested` | ASI01–ASI10, ATLAS technique IDs |
| **Interoperates with** | Import/export round-trip tested | round-trip suite | OTel, OCSF, Inspect logs |
| **Aligned with** | Informative; followed the *intent*; **no** coverage claim | written rationale | NIST AI RMF, ISO/IEC 42001 |
| *(banned)* | "compliant", "certified", "secure", "covers all of" | — | enforced by a **claims linter** |

Regulatory wording: **"produces evidence relevant to Art. 15"**, never "satisfies Art. 15."

### Master standards table
| Standard (version / as-of) | Relationship | Where it shows up | Owning feature | Metric |
|---|---|---|---|---|
| OWASP Top 10 for Agentic Apps 2026 (ASI01–10, 2025-12-09) | Maps to | pack tags, heat-map | F101, F53 | ASI coverage ≥ 9/10 with efficacy-verified pack |
| OWASP Top 10 for LLM Apps 2025 | Maps to | pack tags | R10 | 100% packs tagged |
| OWASP AIVSS v0.8 → v1.0 | Interoperates | per-finding severity vector | F41, F95 | 100% findings carry vector |
| OWASP AI Testing Guide | Aligned | methodology mapping | docs | mapping table published |
| MITRE ATLAS v5.x (agentic) | Maps to | pack/case tags | R10 | ≥ 70% agent-relevant techniques drilled; rest `untested` |
| MITRE ATT&CK (Enterprise) | Maps to | infra-level cases | R10 | tagged where applicable |
| NIST AI RMF 1.0 + GenAI Profile | Aligned | MEASURE-function evidence | F24 | evidence index |
| NIST AI 100-2 (agent additions — **verify**) | Maps to | taxonomy tags | F24 | tag coverage |
| NIST SP 800-53 + COSAIS overlays (**in development**) | Aligned→Maps (when final) | control-evidence export | F100 | overlay-control mapping |
| NIST CAISI / AgentDojo-Inspect | Interoperates | import/export; methodology | F28 | submit ≥1 dataset |
| UK AISI Inspect (`.eval` logs, sandboxing) | Interoperates | import/export | R9 | round-trip |
| ISO/IEC 42001, 27001 | Aligned | evidence export | F24 | evidence index |
| EU AI Act (Reg. 2024/1689; Omnibus Reg. 2026/1744) | Aligned (Art. 9/12/15 evidence) | agentcomply export | F24 | evidence index per article |
| CSA AI Controls Matrix (AICM); MAESTRO layers | Maps to | control + layer tags | F93 | layer coverage |
| AIUC-1 (agent certification — **verify scope**) | Aligned | evidence index | F96 | evidence index |
| SARIF 2.1.0 | **Conforms to** | PR annotations | F100 | 100% schema-valid |
| OpenTelemetry GenAI semconv (Development) | Interoperates (version-pinned) | traces/metrics | F100 | pin recorded; ≥95% span coverage |
| OCSF, ECS | Interoperates | SIEM findings | F100 | round-trip |
| STIX 2.1 / TAXII | Interoperates | adversary cards, intel intake | F94 | valid bundle |
| OSCAL (assessment-results, POA&M) | **Conforms to** (profile) | exposure ledger export | F95 | validates |
| in-toto + SLSA; Sigstore | **Conforms to** | attestations, signatures | F96, F35 | verify OK in verifier |
| CycloneDX / SPDX (AIBOM, SBOM) | Conforms to | release SBOM; pack BOM | DD-25 | validates |
| CVSS v4.0 | Conforms to | per-finding base vector | F41 | 100% |
| MCP spec (dated revisions), A2A 1.0 | Conforms to (client/server fidelity) | protocol drivers | F103 | revision pins |
| OpenSSF Scorecard / Best Practices | Aligned→Conforms | repo hygiene | existing | Scorecard target (**verify scale**) |

### OWASP ASI coverage (2026)
| ID | Risk | Coverage (estimate — verify) | Gap → feature |
|---|---|---|---|
| ASI01 | Agent Goal Hijack | Covered | recursive/cross-context variants (F101) |
| ASI02 | Tool Misuse & Exploitation | Covered | chained-safe-tools-unsafe-sequence (F89) |
| ASI03 | Identity & Privilege Abuse | Partial | OAuth/confused-deputy, identity inheritance (F101) |
| ASI04 | Agentic Supply Chain | Covered | dynamic detonation (F98) |
| ASI05 | Unexpected Code Execution | Partial | code-agent/eval paths; escape-to-host (F101) |
| ASI06 | Memory & Context Poisoning | Partial | persistence, cross-tenant bleed (F101) |
| ASI07 | Insecure Inter-Agent Communication | Thin | ungate A2A 1.0; card forgery (F101) |
| ASI08 | Cascading Agent Failures | **None** | fault-propagation, containment (F101) |
| ASI09 | Human-Agent Trust Exploitation | **None** | approval fidelity, persuasion (F101) |
| ASI10 | Rogue Agents | Thin | oversight subversion, goal drift (F101) |

### MITRE ATLAS (agent-relevant; IDs from secondary sources — **verify**)
| Technique (as reported) | Candidate ID | Case class |
|---|---|---|
| AI Agent Context Poisoning (incl. Memory sub-technique) | AML.T0080 (.000) | memory poisoning, cross-session persistence |
| Modify AI Agent Configuration | AML.T0081 | rules/instruction-file tampering |
| RAG Credential Harvesting | AML.T0082 | retrieval credential exfil |
| AI Agent Tool Data Poisoning | AML.T0099 | tool-output poisoning |
| Data Destruction via AI Agent Tool Invocation | AML.T0101 | destructive-command |
| Exfiltration via AI Agent Tool Invocation | AML.T0062 *or* T0086 (**conflict**) | exfil chain |
| Tool-Chain Poisoning | AML.T0091 | MCP/skill supply chain |
| Memory Persistence Across Sessions | AML.T0094 | persistence |
| Publish Poisoned AI Agent Tool (Feb 2026) | (**verify**) | rug-pull / poisoned registry |
| Escape to Host (Feb 2026) | (**verify**) | sandbox escape |
| Mitigations: *Restrict AI Agent Tool Invocation on Untrusted Data*, *Human In-the-Loop for AI Agent Actions*, *AI Agent Tool Permissions Configuration*, *Memory Hardening* | — | map **defenses** to ATLAS mitigations |

ATT&CK (infra-level): T1195, T1059, T1041/T1567, T1552, T1611, T1485, T1496 (**verify each**). D3FEND: map defenses to countermeasure classes (P2). CAPEC/CWE: finding-level; enables a CVE/CNA path ([PRD 37](37-break-it-program.md)).

### NIST & government
| Source | Relationship | What we take |
|---|---|---|
| NIST AI RMF 1.0 + GenAI Profile | Aligned | MEASURE-function (TEVV) evidence index with `not evidenced` rows |
| NIST AI 100-2 (agent additions — **verify**) | Maps to | taxonomy tags |
| NIST SP 800-53 + COSAIS (agent use cases; concept paper Aug 2025; in development) | Aligned→Maps | defense contracts declare 800-53 controls; drills are control-effectiveness evidence |
| NIST SP 800-218A | Aligned | our own SSDF practices (signed releases, SBOM) |
| NIST CAISI (AgentDojo-Inspect, hijacking insights; cheating-on-agent-evals note) | Interoperates + Participates | adaptive + multi-attempt methodology (F85/F86); meta-verification (F43); submissions (F28) |
| UK AISI Inspect (`.eval` logs, sandboxing) | Interoperates | import/export; submit packs as Inspect tasks |
| IETF BMWG *Security Evaluation Benchmark for AI Agents* draft | Participates | offer methodology review |
| CISA/NSA AI deployment & data-security guidance | Aligned | map recommendations to drillable controls |
| NIST CSF 2.0 (+ AI profile — **verify**) | Aligned | tag findings to functions |
| NIST SP 800-61 / 800-115 | Aligned | RoE + report structure ([PRD 35](35-rules-of-engagement-and-safe-fire.md)) |

### ISO/IEC, EU AI Act & assurance
| Standard / regime | Relationship | Notes |
|---|---|---|
| ISO/IEC 42001 | Aligned | certifiable AI management system; Annex A evidence (risk assessment, V&V, incident response) |
| ISO/IEC 27001 / 27002 | Aligned | ISMS; drills as operational-control evidence |
| ISO/IEC 23894 | Aligned | AI risk-management methodology |
| ISO/IEC 29147 / 30111 | Aligned | vulnerability disclosure basis ([PRD 37](37-break-it-program.md)) |
| ISO/IEC 5338 / 27090-type (in development — **verify**) | track | — |
| EU AI Act: Annex III high-risk **2027-12-02**, Annex I **2028-08-02**, Art. 50 **2026-08-02** (Omnibus Reg. (EU) 2026/1744, in force 2026-07-27); GPAI systemic-risk (Art. 55) in force | Aligned (evidence Art. 9/12/15) | dates from secondary summaries — **confirm with counsel** |
| CRA / NIS2 / DORA | Aligned | disclosure + resilience-test evidence; CRA reporting dates **verify** |
| CSA AICM (≈243–247 controls / 18 domains — **verify**) + STAR for AI | Maps to | evidence export |
| AIUC-1 | Aligned | PI-F10 attestation could feed assessment (**verify scope**) |
| Google SAIF, Databricks DASF, Pillar SAIL | Aligned | informative |

**Evidence-index product requirement:** per-release `clause/control → drills → date → config digest → outcome → what is NOT evidenced` (last column mandatory).

### Interchange & supply chain
| Standard | Role | Level |
|---|---|---|
| SARIF 2.1.0 | PR annotations, code scanning, IDE | Conforms |
| JUnit XML | CI reporting (`missed`→failure, `untested`→skipped) | Conforms |
| OCSF / ECS | SIEM/lake findings | Interoperates |
| STIX 2.1 / TAXII | adversary cards, intel | Interoperates |
| OSCAL (assessment-results, POA&M) | GRC; ledger export | Conforms (profile) |
| Inspect/`promptfoo`/`garak`/`AgentDojo`/`PyRIT` | import/export | Interoperates |
| OTel GenAI semconv + MCP conventions; W3C Trace Context | telemetry | Interoperates (semconv pinned) |
| in-toto + SLSA (target Build L3 — **verify**) | provenance | Conforms |
| Sigstore | signing/verification | Conforms |
| CycloneDX (incl. ML-BOM/AIBOM) / SPDX 3.x; VEX | SBOM/VEX | Conforms |
| CVSS v4.0 + AIVSS; SSVC | severity/prioritization | Conforms / Interoperates |
| JSON Schema 2020-12; semver 2.0; SHA-256 pack IDs | pack format | Conforms |

### Standards participation (moat, per F28)
Submit/engage: OWASP ASI (pack/test mappings), MITRE ATLAS (observed techniques), NIST CAISI (datasets), UK AISI Inspect (tasks), IETF BMWG draft (methodology), OTel GenAI SIG (security attributes). **Target:** ≥ 1 accepted external contribution/year; ≥ 1 per release in review.

## Dependencies
R10, F24, F28, F41, F43, F53, F79–F84 · [PRD 34](34-drill-attestations-and-deploy-gate.md), [PRD 38](38-security-ecosystem-integrations.md), [PRD 39](39-frontier-attack-classes.md), [PRD 41](41-platform-compatibility.md), [PRD 43](43-evidence-register-and-method.md).

## Boundaries & non-goals
- agentdrill is a **testing instrument**, not a compliance product; compliance mapping lives in agentcomply (F24).
- We *tag* and *map*; we do not certify.

## Open questions
1. Confirm NIST AI 100-2 agent additions and COSAIS overlay status (verify before claiming mapping).
2. Is there an OWASP-endorsed "Maps to ASI" declaration process? If not, publish mapping repo for review.
