# Extension Detonation, Break-It & Frontier Attack Classes — Design

**BLUF:** Detonate unknown third-party extensions in the hermetic lab; invite a crowd to break the reference
range; and ship the attack classes that close the OWASP ASI gaps. WBS
[M29](../wbs/v0.1.0/wbs-v0.1.0-part16-frontier-platform-standards.md). Reference:
[PRD 36](../prd/36-extension-detonation-lab.md), [PRD 37](../prd/37-break-it-program.md),
[PRD 39](../prd/39-frontier-attack-classes.md).

> **Built (M29).** Packages: `agentdrill/detonation/` (`behavior.py`), `agentdrill/breakit/` (`program.py`,
> `corpus.py`), `agentdrill/frontier/` (`classes.py`). See the
> [reference](../reference/detonation-breakit-frontier.md). Rewritten against the built system at M31–M32.

## Extension detonation (F98)

Run an unknown **extension** (MCP server stdio/HTTP; skill; plugin/hook; rules/instruction file; agent
template; package registering tools) in the lab with canaries/sinks and a scripted **driver agent** that
exercises advertised functions. Observe (via M23 witnesses): egress/DNS, honey-file reads, out-of-scope
writes, process spawn, **metadata drift**, **conditional behavior**, agent-directed injection content,
declared-vs-actual mismatch. Output: a **Behavior Report** with evidence refs, per-ATLAS/ASI tags, policy
suggestions, a **prior-version diff** (rug-pull watch), and honest labels (*conditions covered / not covered;
absence of evidence ≠ safe*). Optional signed attestation (F96) as a registry admission artifact.

**Evasion awareness:** multi-schedule runs (time-shifted, repeated, varied personas) reported as coverage.

## Break-It program (F99)

Pinned **reference configs** in a RoE-governed range → structured **proof-of-bypass** (route, effect goal)
**auto-verified by the witness** → triage SLA + CVSS v4.0 + AIVSS severity + **family dedup** (F89) →
coordinated disclosure (private fix window 30–90 d, embargo, credit, CVE/CNA + CWE) → rewards → **convert
accepted bypass to a permanent regression** (F61) + route-family catalogue + optional ATLAS submission.
Import public human-found corpora (e.g., ART benchmark — license check). Start as a **pilot**.

## Frontier attack classes (F101)

Each ships as a pack class with benign twins + witnesses + cleanup:

| # | Class | ASI / ATLAS | Validates |
|---|---|---|---|
| 1 | HITL / approval abuse (lies-in-the-loop) | ASI09 | approval fidelity, step-up (CIBA/CDA), diff rendering |
| 2 | Computer-use / browser | ASI01/02/05 | browser sandbox, domain allowlist, form-fill guard |
| 3 | Multimodal injection | ASI01 | content normalization, egress/tool gating |
| 4 | Identity, delegation & OAuth | ASI03 | broker scoping, RFC 8707 audience, task-scoped tokens |
| 5 | Memory & persistence | ASI06 | memory hardening, provenance tags, isolation |
| 6 | Multi-agent cascade & rogue agents | ASI07/08/10 | delegation limits, circuit breakers, containment, halt |
| 7 | Resource exhaustion / denial-of-wallet | LLM10 | budget enforcement, rate limits, kill-time |
| 8 | AP2 payments (spec-gated, P2) | ASI03 | payment guardrails |

## Invariants

1. Documented patterns only; rogue/self-modification framed as **oversight subversion**, not capability uplift.
2. Extension detonation runs in strict isolation (VM/microVM), RoE-governed, **no real egress**; a clean
   report is bounded evidence, never "safe".
3. Break-It accepted payloads stay private until fix + embargo; published artifacts are family-level.
4. Dual-use review sign-off per class.

## Open questions
1. Seeded-corpus provenance (documented incidents only).
2. Host the range ourselves vs. partner (Gray Swan/HackerOne-class).
3. Publish a public "extension behavior" feed?
