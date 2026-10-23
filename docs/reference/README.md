# Reference

Normative reference for agentdrill — CLI, formats, compatibility, errors, policies. Design intent until the
build lands (v0.1.0 planned).

| Document | Scope | Status |
|---|---|---|
| [cli-reference.md](cli-reference.md) | Command surface + output/exit codes | draft |
| [pack-format-spec.md](pack-format-spec.md) | Normative attack-pack schema | **normative (M2)** |
| [pack-catalog.md](pack-catalog.md) | The v0.1.0 pack catalog + fixtures | **normative (M2)** |
| [run-artifact-spec.md](run-artifact-spec.md) | Run / per-case artifact schema | **normative (M3)** |
| [failure-taxonomy.md](failure-taxonomy.md) | Outcomes, dimensions, oracle catalog, divergence | **normative (M6)** |
| [evidence-and-telemetry.md](evidence-and-telemetry.md) | agentwatch reader, binding, telemetry-gap, coverage | **normative (M7)** |
| [determinism-methodology.md](determinism-methodology.md) | How each oracle decides blocked/missed/degraded; pins, fixtures, contamination | **normative (M8)** |
| [reporting-and-statistics.md](reporting-and-statistics.md) | Report formats, honesty rules, statistics policy, benchmark schema | **normative (M10)** |
| [adapter-api.md](adapter-api.md) | Driver + target adapter API | **drivers normative (M4)** |
| [custom-adapter-guide.md](custom-adapter-guide.md) | Build + register a custom driver | **normative (M4)** |
| [compatibility.md](compatibility.md) | Harness × version compatibility | draft |
| [errors.md](errors.md) | Error contract + exit codes | draft |
| [known-limitations.md](known-limitations.md) | Honest limitations | draft |
| [versioning-policy.md](versioning-policy.md) | Semver + pack-format policy | draft |
| [backwards-compatibility-policy.md](backwards-compatibility-policy.md) | What may change, when | draft |
| [framework-recipes.md](framework-recipes.md) | Tier-2 framework recipes | draft |
| [standards-participation.md](standards-participation.md) | ATLAS/OWASP/NIST/CAISI participation | draft |
| [tech-stack.md](tech-stack.md) | Runtime + tooling | draft |

> The **pack-format** contract is drafted in [../design/pack-format.md](../design/pack-format.md) and is
> **normative** for the schema/loader/resolution/hashing (M2); runtime semantics become normative with their
> milestones. The **agentwatch record + security-event schema** is an external contract — see
> [agentwatch](https://github.com/agentic-suite/agentsec-agentwatch).
