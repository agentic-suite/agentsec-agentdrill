# Compliance Matrix — v0.1.0

**Status:** ✅ **published** 2026-10-25. Every mapping below is a **Maps to** or **Aligned with** claim, with
its gaps stated. agentdrill does not claim **conformance** or any certification; the claim vocabulary is
[PRD 42](../../prd/42-standards-and-claims.md) and the claims linter (`src/agentdrill/standards/claims.py`) enforces it.

**Claim vocabulary.** **Conforms to** (normative spec, tested) · **Maps to** (tagged, coverage incl. gaps
published) · **Interoperates with** (round-trip tested) · **Aligned with** (informative). The words
"compliant", "certified", and "secure" are **banned** unless quoted or negated.

## Framework mappings (index)

| Document | Framework | Claim | Status |
|---|---|---|---|
| [owasp-llm-agentic.md](../../compliance/owasp-llm-agentic.md) | OWASP LLM Top-10 (2025) + Agentic Apps 2026 (ASI01–ASI10) + AIVSS | Maps to | published |
| [atlas-mapping.md](../../compliance/atlas-mapping.md) | MITRE ATLAS (agentic techniques + mitigations) | Maps to | published |
| [nist-ai-rmf.md](../../compliance/nist-ai-rmf.md) | NIST AI RMF + GenAI Profile + CAISI/AISI | Aligned with | published |
| [eu-ai-act.md](../../compliance/eu-ai-act.md) | EU AI Act (Art. 9/12/15) | Aligned with | published |
| [openssf-badge.md](../../compliance/openssf-badge.md) | OpenSSF Best Practices baseline | Aligned with | published |

## OWASP ASI 2026 coverage (gaps explicit)

Coverage is a **Maps to** claim: packs are tagged and this table publishes the gaps. `None`/`Thin` rows are
real gaps, listed rather than hidden ([PRD 42](../../prd/42-standards-and-claims.md), [PRD 39](../../prd/39-frontier-attack-classes.md)).

| ID | Risk | Coverage | Gap → feature |
|---|---|---|---|
| ASI01 | Agent Goal Hijack | Covered | recursive/cross-context variants |
| ASI02 | Tool Misuse & Exploitation | Covered | chained-safe-tools-unsafe-sequence |
| ASI03 | Identity & Privilege Abuse | Partial | OAuth/confused-deputy, identity inheritance |
| ASI04 | Agentic Supply Chain | Covered | dynamic detonation |
| ASI05 | Unexpected Code Execution | Partial | code-agent/eval paths; escape-to-host |
| ASI06 | Memory & Context Poisoning | Partial | persistence, cross-tenant bleed |
| ASI07 | Insecure Inter-Agent Communication | Thin | A2A 1.0 ungate; card forgery |
| ASI08 | Cascading Agent Failures | **None** | fault-propagation, containment |
| ASI09 | Human-Agent Trust Exploitation | **None** | approval fidelity, persuasion |
| ASI10 | Rogue Agents | Thin | oversight subversion, goal drift |

**Covered: 3 · Partial: 3 · Thin: 2 · None: 2.** No ASI category is omitted, and none is reported as fully
covered when it is not.

## Per-framework evidence index (v0.1.0)

The field test drove the **same packs** through eight real agent frameworks (Track B, 19 agents). Coverage is
stated at the level the run actually proves; `not covered` is always listed.

| Framework | Driven (real loop) | Witnessed (L3) | Not covered |
|---|---|---|---|
| LangGraph | ✅ | ✅ (demo suites) | L4 gated contract pack; no in-CI contract run for this framework |
| OpenAI Agents SDK | ✅ | ✅ | L4 contract pack |
| AutoGen (AG2) | ✅ | ✅ | L4 contract pack |
| CrewAI | ✅ | ✅ | L4 contract pack |
| Google ADK | ✅ | ✅ | L4 contract pack |
| PydanticAI | ✅ | ✅ | L4 contract pack |
| smolagents | ✅ | ✅ | L4 contract pack |
| LlamaIndex | ✅ | ✅ | L4 contract pack |

- **Driven (L2):** every framework executed the packs through a real agent loop; skip counts as failure
  ([field test report](../../field-test/v0.1.0/FIELD_TEST_REPORT.md), Track B 19/19).
- **Witnessed (L3):** the demo suites record an independent witness verdict ([PRD 26](../../prd/26-independent-effect-witness.md)).
- **Not covered:** no framework is at **L4 (gated contract pack in CI)** in v0.1.0. That is a declared gap, not
  an implied pass.

## OpenSSF baseline

Baseline artifacts are collected in [openssf-badge.md](../../compliance/openssf-badge.md): security policy,
SBOM + signed provenance, the deterministic quality gate (`ruff`, `mypy --strict`, coverage ≥95%), threat model,
assurance case, and private vulnerability reporting. The OpenSSF Scorecard workflow
(`.github/workflows/scorecard.yml`) produces the grade on the default branch; the grade is recorded there, not
asserted here.

## What is not covered (consolidated)

- **ASI08, ASI09: none.** Cascading-failure containment and human-agent trust exploitation have no
  efficacy-verified pack yet.
- **ASI07, ASI10: thin.** Inter-agent communication and rogue-agent oversight are partially exercised.
- **L4 gating: no framework.** No contract pack runs in CI for any harness yet.
- **A2A / inter-agent peers:** not driven in v0.1.0.

See the [claims ledger](../claims-ledger.md) for the full list of public claims and their evidence artifacts.
