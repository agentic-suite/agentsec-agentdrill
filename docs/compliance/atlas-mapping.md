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

## Agentic techniques (2026 updates; IDs from secondary sources — **verify**)

| Technique | Candidate ID | Pack classes |
|---|---|---|
| AI Agent Context Poisoning (incl. Memory sub-technique) | AML.T0080 (.000) | memory poisoning, cross-session persistence |
| Modify AI Agent Configuration | AML.T0081 | rules/instruction-file tampering |
| RAG Credential Harvesting | AML.T0082 | retrieval credential exfil |
| AI Agent Tool Data Poisoning | AML.T0099 | tool-output poisoning |
| Data Destruction via AI Agent Tool Invocation | AML.T0101 | destructive-command |
| Exfiltration via AI Agent Tool Invocation | AML.T0062 *or* T0086 (**verify**) | exfil chain |
| Tool-Chain Poisoning | AML.T0091 | MCP/skill supply chain |
| Memory Persistence Across Sessions | AML.T0094 | persistence |
| Publish Poisoned AI Agent Tool | (**verify**) | rug-pull / poisoned registry |
| Escape to Host | (**verify**) | sandbox escape |

ATT&CK (infra-level): T1195, T1059, T1041/T1567, T1552, T1611, T1485, T1496 (**verify each**). Findings
also map to **CWE/CAPEC** at the implementation level, enabling a CVE/CNA path ([PRD 37](../prd/37-break-it-program.md)).

## Defenses are mapped to ATLAS mitigations

Beyond attack tactics, we tag the **ATLAS mitigation** each defense is meant to implement (*Restrict AI Agent
Tool Invocation on Untrusted Data*, *Human In-the-Loop for AI Agent Actions*, *AI Agent Tool Permissions
Configuration*, *Memory Hardening*) — so the heat-map answers "which mitigations are proven vs. `untested`".

## Rule

The **coverage heat-map** (F53) is organized by ATLAS tactic/mitigation × control — so an unpublished tactic
shows as `untested`, never omitted.
