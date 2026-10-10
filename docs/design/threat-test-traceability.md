# Threat → Drill Traceability

**BLUF:** Every threat in agentdrill's [threat model](threat-model.md) maps to a control and to the **drill
case** that proves the control works. Untested threats are `untested` in the coverage heat-map — never
silently omitted.

> **Design intent** (pre-build). Populated as the evasion and meta-verification packs land (M14).

| Threat | Control | Drill (pack/case) | Status |
|---|---|---|---|
| Pack tamper | Signature + hash check | `evasion-self-attack/tamper-pack` | planned (M14) |
| Hook disable | Config/hook integrity check | `evasion-self-attack/hook-disable` | planned (M14) |
| Policy edit → always-allow | CI gate on the compiled policy | `evasion-self-attack/policy-edit` | planned (M14) |
| Telemetry injection | Untrusted-input handling | `evasion-self-attack/telemetry-inject` | planned (M14) |
| Evidence edit | Manifest/hash binding | `evasion-self-attack/evidence-edit` | planned (M14) |
| Update hijack | Signed, pinned updates | `evasion-self-attack/update-hijack` | planned (M14) |
| Agent-instructed evasion | Enforcement outside agent control plane | `evasion-self-attack/agent-evasion` | planned (M14) |
| Oracle gaming | Drill-the-drill meta-verification | `meta-verification/vacuous-noop`, `meta-verification/exit-code` | planned (M14) |
| Registry poisoning | Signed publisher + trust level | `meta-verification/registry-poison` | planned (M16) |
| Adaptive overreach | Mutation caps + review gate | `meta-verification/adaptive-boundary` | planned (M15) |

> **Rule:** a threat with no passing drill is published as `untested`, with a reason — the same discipline
> as the honest-coverage table.
