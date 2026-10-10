# OWASP LLM Top-10 + OWASP Agentic AI Mapping

Every attack pack/attack maps to OWASP categories (tag-enforced). Design intent.

## OWASP LLM Top-10 (2025)

| Risk | Pack classes |
|---|---|
| LLM01 Prompt Injection | `incidents-security` (prompt injection), exfil chains |
| LLM02 Sensitive Information Disclosure | exfil chain, credential evasion |
| LLM03 Supply Chain | Plugin4Shell-style supply chain, skill/capability content-swap |
| LLM05 Improper Output Handling | destructive-command (output → side effect) |
| LLM06 Excessive Agency | destructive-command, over-permission cases |
| LLM07 System Prompt Leakage | system-prompt extraction cases |
| LLM10 Unbounded Consumption | DoS/budget-exhaustion chains |

## OWASP Top 10 for Agentic Applications 2026 (ASI01–ASI10)

Published 2025-12-09. Coverage is declared with gaps; a category without an efficacy-verified, witnessed
pack shows `untested`, never omitted ([PRD 39](../prd/39-frontier-attack-classes.md),
[PRD 42](../prd/42-standards-and-claims.md)).

| ID | Risk | Pack classes / coverage |
|---|---|---|
| ASI01 | Agent Goal Hijack | injection / Slack-AI exfil / tool poisoning; + recursive & cross-context (F101) |
| ASI02 | Tool Misuse & Exploitation | destructive-command, MCP poisoning, argument binding; + chained-safe-tools (F89) |
| ASI03 | Identity & Privilege Abuse | credential evasion; + OAuth/confused-deputy, identity inheritance (F101) |
| ASI04 | Agentic Supply Chain | Plugin4Shell, skill content-swap, rug-pull; + dynamic detonation (F98) |
| ASI05 | Unexpected Code Execution | sandbox-escape; + code-agent/eval, escape-to-host (F101) |
| ASI06 | Memory & Context Poisoning | + persistence across sessions, cross-tenant bleed (F101) |
| ASI07 | Insecure Inter-Agent Communication | + A2A 1.0 card forgery, delegation smuggling (F101) |
| ASI08 | Cascading Agent Failures | + fault-propagation, containment (F101) |
| ASI09 | Human-Agent Trust Exploitation | + approval fidelity, persuasion, step-up (F101) |
| ASI10 | Rogue Agents | evasion pack (own tools); + oversight subversion, goal drift (F101) |

**Targets:** ≥6/10 ASI categories efficacy-verified + witnessed at v0.1.0; ≥9/10 by v0.2.

## OWASP AIVSS (agentic severity)

Per-finding severity is **CVSS v4.0 + an AIVSS amplification vector** (autonomy, tools, language, context,
non-determinism, opacity, persistence, identity, multi-agent, self-modification) — **never aggregated into a
single score** ([PRD 42](../prd/42-standards-and-claims.md), DD-41).

## Rule

A pack/attack without at least one valid ASI/LLM tag fails **lint** — coverage is declared with `untested`
gaps, never implied.
