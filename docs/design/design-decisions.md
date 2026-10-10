# agentdrill — Design Decisions

Centralized decision log. Referenced as `DD-NN`. Mirrors [PRD 11](../prd/11-decisions.md); accepted at
design time (2026-10-09), pending build.

## Accepted

| ID | Decision | Status | Rationale |
|---|---|---|---|
| DD-01 | **agentdrill owns no enforcement** — it drives the deployed stack and reads evidence | accepted | A drill that enforced would test itself, not the user's stack |
| DD-02 | **Targets are the deployed stack**, not a simulation | accepted | R2; results must reflect the real enforcement path |
| DD-03 | **No ground-truth leakage** — oracles/expected outcomes never sent to the driver | accepted | A drill you can read the answer to is not a drill |
| DD-04 | **Deterministic oracles first, LLM judge only where needed** | accepted | Cheap, reproducible, offline-safe |
| DD-05 | **Reuse the agentwatch record + security-event schema** for machine-readable results | accepted | Single source of truth across the ecosystem |
| DD-06 | **Honest reporting is mandatory** — a run cannot publish without its misses | accepted | The differentiator (R5) |
| DD-07 | **Two-layer oracle discipline** (deterministic vs judge fail differently) | accepted | Divergences flagged, not averaged |
| DD-08 | **Harness-agnostic or explicitly harness-compatible**; per-harness packs where needed | accepted | Ecosystem non-negotiable |
| DD-09 | **Custom oracles/adapters via a plugin registry**, validated at load | accepted | Extensibility without forking |
| DD-10 | **Adversarial self-test is shipped, not optional** (evasion pack) | accepted | Own-threat-model operationalized (R7) |
| DD-11 | **v0.1.0 = Wave 0**: incident-replay packs + CI gate + honest benchmark + kill-time + evasion | accepted | Matches the release-roadmap meta-MVP |
| DD-12 | **Replay documented incidents only** — no novel model-attacking capability | accepted | Dual-use boundary |
| DD-13 | **No injection-detection claims** from drill results | accepted | We measure controls |
| DD-14 | **Import interop (promptfoo/garak/AgentDojo/PyRIT)** — reuse the community's suites | accepted | Don't reinvent (R9) |
| DD-15 | **Python core** (library + CLI + pytest plugin), shared runner/oracle/adapter engine | accepted | One engine, three surfaces |
| DD-16 | **YAML attack packs** (JSON secondary) | accepted | Authoring ergonomics; absorbed pack format |
| DD-17 | **`pip install agentsec-agentdrill`**, CLI `agentdrill` | accepted | Ecosystem naming convention |
| DD-18 | **Pinned seeds/models + `run-manifest.json`**; re-pin ⇒ re-publish | accepted | Reproducibility is the success bar (R6) |
| DD-19 | **Local JSON artifacts under `.agentdrill/`** | accepted | Local-first |
| DD-20 | **Sandbox + trust levels + audit + secret sanitization** for untrusted packs | accepted | Community packs are executable |
| DD-21 | **MITRE ATLAS + OWASP tagging on every pack/attack** | accepted | R10; standards posture |
| DD-22 | **Apache-2.0 license** | accepted | Ecosystem standard |
| DD-23 | **Packs reviewed like code** (community flow) | accepted | Packs are executable security claims |
| DD-24 | **Public methodology or nothing** — no proprietary scoring | accepted | Trust |
| DD-25 | **Signed packs + provenance** on release | accepted | Supply-chain trust |
| DD-26 | **Each release ships notes + compatibility table + security audit + published benchmark** | accepted | Org governance floor + R4/R5 |
| DD-27 | **A single run is never a claim** — mean ± std over ≥3 seeds; CIs; p50/p95 on kill-time | accepted | Benchmark-trust posture |
| DD-28 | **Flag, never silently fix** — preregistered goldens; changes flagged with a re-pin note | accepted | Trust posture |
| DD-29 | **Dark holdout** — unpublished holdout subset in CI | accepted | Anti-pack-gaming |
| DD-30 | **Contamination disclosed, not hidden** | accepted | SWE-Bench lesson |
| DD-31 | **Limitations register ships with every release** | accepted | agentwatch discipline |
| DD-32 | **Signed provenance on published artifacts** — Sigstore signatures + provenance | accepted | Supply-chain trust |

## Accepted — world-class additions (2026-10-10, PRDs 25–42)

| ID | Decision | Status | Rationale |
|---|---|---|---|
| DD-35 | **Effects are adjudicated by witnesses outside the defended stack**; defense-vs-witness disagreement is a first-class finding | accepted | Removes circular oracles; makes stealth attacks visible ([PRD 26](../prd/26-independent-effect-witness.md)) |
| DD-36 | **Every published number carries an attacker tier + `Hold@k`/`ASR@k` + CI**; no bare "blocked %" | accepted | Static replay ≠ robustness ([PRD 25](../prd/25-attacker-strength-and-pressure.md)) |
| DD-37 | **Adversary Lab is loopback-only, seed-deterministic, documented-pattern-only, signed** | accepted | Fidelity + dual-use boundary ([PRD 27](../prd/27-adversary-lab.md)) |
| DD-38 | **agentdrill is neutral: drills any defense; head-to-heads carry no composite score or ranking** | accepted | Independence is the moat ([PRD 29](../prd/29-bring-your-own-defense.md)) |
| DD-39 | **Waivers annotate, never relabel**; a miss stays `missed`; integrity findings are not waivable | accepted | Keeps the gate livable without scoring theater ([PRD 33](../prd/33-exposure-ledger-and-waivers.md)) |
| DD-40 | **Rules of engagement are required for any non-demo run**; destructive effects are canary-only; global abort is independent of the system under test | accepted | Protects targets/bystanders; dual-use posture ([PRD 35](../prd/35-rules-of-engagement-and-safe-fire.md)) |
| DD-41 | **Per-finding severity is CVSS v4.0 + an AIVSS vector; never aggregated into a score** | accepted | Buyer expectation without a composite ([PRD 42](../prd/42-standards-and-claims.md)) |
| DD-42 | **Claim vocabulary is enforced by a linter**; "compliant/certified/secure" are banned | accepted | Prevents over-claim ([PRD 42](../prd/42-standards-and-claims.md)) |
| DD-43 | **Platform compatibility is a graded scale (L0–L4)** with a reference-harness policy and AWC | accepted | "Compatible" must be measured ([PRD 41](../prd/41-platform-compatibility.md)) |

## Deferred (direction accepted, finalize during the build)

| ID | Decision | Direction |
|---|---|---|
| DD-33 | Re-pin cadence when a pinned model drifts/dies | Define a schedule that keeps packs meaningful; re-publish with a manifest note |
| DD-34 | Dual-use boundary for mutation/adaptive content | Mutation-of-documented-patterns only; review gate for shipped packs |
| DD-44 | **T3 adaptive attacker tier** (adaptive search vs. this stack) | Deferred for v0.1.0; local-only, RoE-gated, unpublished when introduced ([PRD 25](../prd/25-attacker-strength-and-pressure.md)) |
| DD-45 | Competitor/other-defense benchmark publication shape | Neutrality rules + right-of-reply + licensed-config-only; counsel review before first publication ([PRD 29](../prd/29-bring-your-own-defense.md)) |

## Template

```
### DD-NN — Title
- **Status:** proposed | accepted | superseded | closed
- **Context:**
- **Decision:**
- **Consequences:**
```
