# Threat Model — agentdrill's Own

**BLUF:** A tool that attacks other software must be the most honest and hardened thing in the stack. This
is agentdrill's **STRIDE-style** threat model — the surfaces an adversary would target (pack catalog,
evidence, published numbers, credentials, the harness itself) and the controls that bound them. The evasion
pack (R7) is this model operationalized as executable tests.

> **Design intent** (pre-build). Rewritten against the built system at M23–M24.

## Assets

| Asset | Why it matters |
|---|---|
| Pack catalog | Executable security claims; tampering changes what "blocked" means |
| Evidence + results | The reproducibility claim; forged results destroy the moat |
| Published benchmark | The trust artifact the whole ecosystem points at |
| Driver/target credentials | Drills touch real enforcers and (brokered) credentials |
| The harness itself | If compromised, the attacker owns the proof |

## Surfaces (STRIDE)

| Surface | Threat | Control |
|---|---|---|
| **Pack catalog** | Tamper a pack so a blocked attack reads blocked-but-isn't | Signatures + hash (F35/F39); tamper → fail-closed |
| **Hooks/adapters** | Edit driver config to silently skip a pack | Config/hook integrity checked; tamper → loud fail |
| **Policy / compiled output** | Edit compiled policy to always-allow | The un-blocking change is rejected by CI (CUJ-2) |
| **Telemetry / evidence** | Injection via crafted tool names/args | Treat telemetry as untrusted input; no eval/dynamic render; `telemetry_gap` |
| **Update channel** | Malicious update re-runs a hostile pack set | Signed, pinned updates; update is a policy decision |
| **Results store** | Edit a published number | Manifest/hash binding (F31); reproduction disputes |
| **Oracle / judge** | Game the scorer without actually blocking | Drill-the-drill (F43); evidence binding; divergence gating |
| **Registry** | Malicious/typo-squatted pack enters the index | Signed packs, verified publishers, trust levels (RK-16) |
| **Adaptive orchestrator** | Drifts into novel-exploit generation | Mutation caps + provenance + review gate (RK-13) |

## Anti-tamper principles (from the ecosystem own-threat-model)

1. **Enforcement lives outside the agent's control plane** — anything the agent can edit/kill is advisory.
2. **Fail-closed on tamper** — integrity failure = block, not warn.
3. **Assume the harness is compromised** — a hijacked harness still cannot extract brokered creds or forge
   evidence past the manifest/hash binding.
4. **Separation of duties** — what holds secrets ≠ what decides ≠ what observes.

## Reserved

Agentdrill's own **escalation channel** (advisory rule → human PR, never auto-applied) and **evidence
auditability** are detailed in [privacy-data-handling](privacy-data-handling.md) and are part of the
critical path; both must be drilled by the evasion pack (M14).
