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

## OWASP Agentic AI Top-10 (drafts)

| Risk | Pack classes |
|---|---|
| Identity confusion | MCP shadowing/rug-pull, cross-server shadow |
| Excessive agency | destructive-command, approval-boundary |
| Memory poisoning | memory/multi-agent abuse pack class |
| Tool misuse | MCP tool poisoning, tool-argument cases |
| Insecure inter-agent communication | multi-agent chaining, A2A (later) |

## Rule

A pack/attack without at least one OWASP tag fails **lint** — coverage is declared, never implied.
