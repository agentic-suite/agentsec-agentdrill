# Architecture Decision Records

Formal, numbered ADRs for agentdrill. The central decision log is
[../design/design-decisions.md](../design/design-decisions.md); the ADRs here are the formalized subset
that fixes an architecture.

| ADR | Title | Status |
|---|---|---|
| [0001](0001-python-core.md) | Python core, one engine across surfaces | accepted |
| [0002](0002-attack-pack-format.md) | Attack packs as YAML with strict validation | accepted |
| [0003](0003-composition-over-enforcement.md) | agentdrill owns no enforcement | accepted |
| [0004](0004-reuse-agentwatch-schema.md) | Reuse the agentwatch record + security-event schema | accepted |
| [0005](0005-no-ground-truth-leakage.md) | Drivers never receive oracles/expected outcomes | accepted |
| [0006](0006-deterministic-oracles-first.md) | Deterministic oracles first; judge only where needed | accepted |
| [0007](0007-efficacy-control.md) | Unguarded control group (efficacy) is mandatory | accepted |
| [0008](0008-kill-time-cessation-probe.md) | Kill-time is a cessation probe, not an event receipt | accepted |
| [0009](0009-signed-packs-trust-levels.md) | Signed packs + enforced trust levels | accepted |
| [0010](0010-license.md) | Apache-2.0 license | accepted |
| [0011](0011-independent-effect-witness.md) | Independent effect witness is a primary oracle input | accepted |
| [0012](0012-rules-of-engagement.md) | Rules of engagement mandatory; destructive effects canary-only | accepted |
| [0013](0013-no-composite-security-score.md) | No composite security score; per-finding CVSS v4.0 + AIVSS only | accepted |
| [0014](0014-graded-platform-compatibility.md) | Graded platform compatibility (L0–L4) + reference-harness policy | accepted |
| [0015](0015-neutral-byod-and-head-to-head.md) | Neutral BYOD; head-to-heads carry no score or ranking | accepted |

## Template

```
# ADR-NNNN — Title
- Status: proposed | accepted | superseded
- Context
- Decision
- Consequences
```
