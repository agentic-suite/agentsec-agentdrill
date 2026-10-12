# PRD 21 — Pack Catalog (v0.1.0)

**BLUF:** agentdrill v0.1.0 ships **7 packs**: 3 absorbed from the predecessor harness (re-pointed from
agent-quality scenarios to defense-proof cases), 1 the evasion/self-attack pack, 1 the meta-verification
pack, 1 the efficacy/control pack, and 1 the quickstart pack — plus the **pack roadmap** for the classes
the incident register and 2026 landscape demand. Every pack carries the efficacy control (F59),
ATLAS/OWASP tags, adversary profiles (F54), and cleanup (F50).

**Status:** Draft — v0.1.0 (2026-10-09) · **Owner:** @deghosal-2026 · **Parent:** agentic-suite #209

## Absorbed from the predecessor harness (re-pointed)

### Pack 1 — `incidents-core` (from `scenarios/core-launch.yaml`)

The 20 launch scenarios across 10 families were agent-quality cases. **The pack is not copied — it is
re-pointed**: each family's *failure mode* becomes a defense-proof case. What tested "did the agent call
the right tool" becomes "does the deployed policy allow/deny this call correctly."

| Absorbed family | → agentdrill case class |
|---|---|
| Tool-argument precision (family 4) | **Policy-argument binding**: policy denies the right tool called with unsafe args (over-broad query, wrong scope), allows the benign twin |
| Disallowed-tool refusal (6) | **Boundary denial**: policy/compiled rules block the disallowed call; benign twin passes; utility-under-attack measured |
| Budget-constrained (8) | **Budget enforcement**: agentkeys/agentpolicy budget rules stop runaway spend mid-chain |
| Recovery (9) | **Fail-closed recovery**: after a denied step, does the stack halt/ask, or does the agent find the un-guarded retry? (seam probe F62) |
| Coding-agent regression (10) | **Coding-agent destructive-command**: Replit-pattern case driven through a Claude Code/Cursor driver |

The fixtures (`scenarios/fixtures/*.json` — 26 tool fixtures) come across as the **fixture corpus** for
deterministic runs (F5), and the pack's `context`/`mode`-driven mock-agent discipline (launch_agents'
`fail:*` modes) becomes the **efficacy-twin harness**: the same driver that runs the guarded case runs
the unguarded twin (F59).

### Pack 2 — `incidents-security` (from `scenarios/security-launch.yaml`)

The 8 security scenarios map almost 1:1 to attack cases against the deployed stack:

| the predecessor harness scenario | → agentdrill case (target · oracle) |
|---|---|
| `prompt-injection-01/02` | Instruction override + system-prompt extraction vs **policyweave-output + agentgate** · `blocked` + `policy-fired` telemetry expected |
| `exfiltration-01/02` | Slack-AI-pattern exfil chain (lookup → external send; credential encode-to-log) vs **agentgate egress + agentkeys** · `blocked` + `secret-detected` |
| `ssrf-01/02` | Metadata-service + internal-endpoint probes vs **agentseatbelt confinement + agentgate** · `blocked` |
| `sandbox-escape-01/02` | Filesystem traversal + container/k8s escape vs **agentseatbelt/agentkernel** · `blocked` + confinement verdict |

These keep their rubric criteria as **judge-oracle criteria** (the LLM-judge layer for refusal/explanation
quality) while gaining deterministic oracles on the enforcer decisions — the hybrid model (PRD 02).

### Pack 3 — `meta-verification` (from `examples/adversarial-pack/`)

The 5 adversarial scenarios tested *the predecessor's own blind spots* (the predecessor's reported harness bugs). They transfer directly as
the **drill-the-drill** pack (F43): can a target fool our oracles the way those bugs let agents fool
the predecessor harness?

| Adversarial case | → agentdrill meta-verification case |
|---|---|
| `adversarial-01-criteria-dead-text` | Judge-oracle criteria must actually reach the judge prompt |
| `adversarial-02-empty-trajectory` | A vacuous no-op target must not score `blocked` |
| `adversarial-03-exit-code` | A must-block miss must exit non-zero (CI gate integrity) |
| `adversarial-04-toolstub-honour-system` | Fixtures must actually intercept (determinism integrity) |
| `adversarial-05-hidden-escape` | The hidden single-layer-escape case (kept **secret within the pack**, JPS independent-reviewer discipline) |

Plus new meta-cases: attestation forgery (F63), evidence-shape forgery, severity-rubric gaming.

## New packs

### Pack 4 — `evasion-self-attack` (R7, F11)

The ecosystem's own threat model as executable tests — targets are **our own tools**:

| Case class | Attack | Expected defense |
|---|---|---|
| Pack tamper | Edit a pack so a blocked attack reads blocked | Signature/hash check fails closed |
| Hook disable | Remove/silence a driver hook | Integrity check at session start; loud fail |
| Policy edit | Tamper compiled policy to always-allow | The un-blocking change is rejected by CI (CUJ-2 is this pack's own acceptance) |
| Telemetry injection | Craft tool names/args that inject into evidence views | Untrusted-input rendering; `telemetry_gap` detected |
| Evidence edit | Modify a stored result/manifest | Hash-chain break detected; reproduction disputes |
| Update hijack | Malicious pack/update channel | Signed, pinned updates; update is a policy decision |
| Evasion attempt | Agent instructed to disable security tooling | Enforcement outside agent's control plane; evasion attempt = high-severity finding |

### Pack 5 — `efficacy-control` (F59)

Not a pack users run for coverage — the pack that runs **against unguarded twins** to efficacy-verify every
other pack's cases. Contains the twin-driver harness, the `attack_inert` flagging, and the
efficacy-report shape. Ships with v0.1.0 because the first published table is meaningless without it.

### Pack 6 — `kill-chain` (R8, F18/F37)

Kill-time and chain-verification cases: destructive command → detect → decide → halt → revoke → probe
`ceased` (the re-attempt probe). Each case declares `max_seconds` and the stage model; publishes p50/p95
per stage. Includes the `cease_gap` cases — revoked-but-still-acting — as the highest-severity class.

### Pack 7 — `quickstart-demo` (F66)

The bundled demo target's mini pack: 5 cases (1 blocked, 1 missed **by design** — the demo must show the
honest-reporting shape, not a fake green), 1 kill-time, 1 seam. Watermarked `demo — never evidence`;
`mock`-attested (F63).

## Pack roadmap (in-scope v0.1.0 classes, from the incident register + 2026 landscape)

| Pack class | Incidents/patterns | Lands |
|---|---|---|
| **MCP attacks** (F19) | Tool poisoning, rug-pull, cross-server shadowing, WhatsApp agent weaponization | v0.1.0 (Wave 1) |
| **Supply chain** (F19) | Plugin4Shell branch-name → auto-update → RCE; capability/skill content-swap; dependency confusion | v0.1.0 |
| **Memory & multi-agent abuse** (F20) | Memory poisoning, stale-context carryover, cross-task leakage, delegation abuse, multi-agent chaining | v0.1.0 |
| **RoguePilot-class** | Dev-machine code exec via coding agent (Copilot 2023 pattern) | v0.1.0 |
| **CI/runner attacks** | Untrusted repo content hijacking agents in CI (CSA Claude Action case) | v0.1.0 |
| **A2A** | Cross-org delegation abuse as spec stabilizes | v0.1.0 (spec-stabilization-gated) |
| **Competitor/other-tools** (R12) | Honest-coverage benchmark packs run against third-party stacks, PR-submitted (F57) | v0.1.0 |

## Catalog rules

1. Every pack: `incident_ref` mandatory, ATLAS/OWASP tags, adversary profile, cleanup, benign twins,
   efficacy-verified before merge (F59/F60 review criteria).
2. Catalog = the public coverage table's rows; a class in the roadmap but not shipped shows as
   `untested` in the heat-map (F53) — never silently omitted.
3. Packs are semver'd registry entries (PRD 17); deprecated packs stay visible with notes.
