# MITRE ATLAS Mapping

Every attack pack/attack carries at least one **ATLAS** technique tag (lint-enforced). Design intent.

| ATLAS tactic | Pack classes |
|---|---|
| Reconnaissance | recon cases (surface probing via agentgate) |
| Resource Development | supply-chain (dependency confusion) |
| Initial Access | prompt injection, CI-runner attacks |
| Execution | destructive-command, code-exec via coding agent (RoguePilot-class) |
| Persistence | hook/skill/plugin content-swap |
| Privilege Escalation | over-permission chains, tool-poisoning |
| Defense Evasion | evasion-self-attack (tamper, hook-disable) |
| Credential Access | credential evasion, agentkeys brokered-secret cases |
| Discovery | MCP surface enumeration |
| Collection | memory poisoning, context bleed |
| Exfiltration | Slack-AI-style exfil chains |
| Impact | destructive-command, DoS/budget exhaustion |

## Rule

The **coverage heat-map** (F53) is organized by ATLAS tactic × control — so an unpublished tactic shows as
`untested`, never omitted.
