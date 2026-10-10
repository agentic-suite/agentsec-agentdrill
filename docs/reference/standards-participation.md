# Standards Participation

**Status:** draft (design intent).

agentdrill tags every pack/attack and maps every published result to the standards that define AI-security
testing — and participates rather than only citing.

## Tagging (required on every pack/attack, R10)

- **MITRE ATLAS** — adversary tactics/techniques for AI systems.
- **OWASP LLM Top-10** (2025).
- **OWASP Agentic AI Top-10** (drafts; identity confusion, excessive agency, memory poisoning).

Lint rejects an untagged pack ([pack-format-spec](pack-format-spec.md) §Validation).

## Mapping (published per release)

- **NIST AI RMF** + Generative AI Profile — governance/risk-tier alignment.
- **EU AI Act Art. 12** — record/log expectations for the evidence trail.
- **ISO 42001 / ISO 27001** — where agent security evidence applies.
- Compliance-mapped reports export to **agentcomply** for evidence automation.

## Submission surface (F28)

- **NIST CAISI** agent-security program — submit packs/results; interop with **AgentDojo-Inspect**
  (agent-hijacking evaluation).
- **OWASP Agentic** — contribute pack classes and coverage mapping.

## Participation posture

- The published benchmark is the ecosystem's **reference** for what agent defenses stop.
- We **import, not replace**: promptfoo/garak/AgentDojo/PyRIT suites are absorbed into packs (R9), and their
  coverage is credited, not rebranded.
