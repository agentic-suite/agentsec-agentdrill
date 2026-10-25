# Standards Participation

**Status:** built (v0.1.0).

agentdrill tags every pack/attack and maps every published result to the standards that define AI-security
testing — and participates rather than only citing.

## Tagging (required on every pack/attack, R10)

- **MITRE ATLAS** — adversary tactics/techniques **incl. the 2026 agentic techniques** and the **ATLAS
  mitigations** each defense implements.
- **OWASP Top 10 for Agentic Applications 2026 (ASI01–ASI10)** — final (published 2025-12-09; no longer "drafts").
- **OWASP LLM Top-10 (2025)**; **OWASP AIVSS** for per-finding severity.

Lint rejects an untagged pack ([pack-format-spec](pack-format-spec.md) §Validation); coverage is published
with `untested` gaps, never implied ([PRD 42](../prd/42-standards-and-claims.md)).

## Claim vocabulary (mandatory)

*Conforms to · Maps to · Interoperates with · Aligned with* — "compliant/certified/secure" are **banned**,
enforced by a **claims linter** over docs/notes/UI ([PRD 42](../prd/42-standards-and-claims.md)).

## Mapping (published per release)

- **NIST AI RMF** + Generative AI Profile — MEASURE-function evidence index with explicit `not covered` rows.
- **NIST SP 800-53 + COSAIS** control overlays (agent use cases; in development).
- **EU AI Act Art. 9/12/15** (post-Omnibus dates) — evidence, not conformity.
- **ISO 42001 / ISO 27001 / ISO 23894 / ISO 29147 / ISO 30111** — where agent security evidence applies.
- Compliance-mapped reports export to **agentcomply** for evidence automation.

## Submission surface (F28)

- **NIST CAISI** agent-security program — submit packs/results; interop with **AgentDojo-Inspect**
  (agent-hijacking evaluation).
- **OWASP Agentic** — contribute pack classes and coverage mapping.

## Participation posture

- The published benchmark is the ecosystem's **reference** for what agent defenses stop.
- We **import, not replace**: promptfoo/garak/AgentDojo/PyRIT suites are absorbed into packs (R9), and their
  coverage is credited, not rebranded.
