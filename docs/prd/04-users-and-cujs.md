# PRD 04 — Users and Critical User Journeys

**BLUF:** agentdrill serves three audiences — the security/platform engineer running agent workloads
(**P2 Ravi**), the ecosystem builder/embedder (**P5 Alex**), and the **public** who read the published
benchmark. The v0.1.0 journeys: run a pack, gate a policy PR, reproduce a published result, drill a named
incident, verify kill-time, run the self-attack pack, and contribute/import a pack.

**Status:** Draft — v0.1.0 (2026-10-09) · **Owner:** @deghosal-2026 · **Parent:** agentic-suite #209

## Users

| Persona | Who | What they need from agentdrill |
|---|---|---|
| **P2 Ravi — security/platform engineer** | Runs agent workloads; owns the deployed enforcement stack (gate, broker, seatbelt/kernel, compiled policy, halt) | Evidence that a config/policy change doesn't un-block a known attack; reproducible numbers for their own stack |
| **P5 Alex — ecosystem builder / embedder** | Builds on agentic-suite; ships tooling that must be trustworthy | A drill harness to regression-test their controls; the honest benchmark to point at |
| **The public** | Practitioners, researchers, procurement, the press | A reproducible, adversarially-reviewed record of what actually stops what — misses included |

## Users this is *not* for

- Teams that want a **detection product** or a "we solve prompt injection" claim — agentdrill measures
  controls, it does not sell detection ([PRD 14](14-non-goals.md)).
- Anyone who wants an **enforcement engine** — agentdrill composes the enforcers.
- Anyone who wants a **model leaderboard** — the benchmark is defenses vs. documented attacks.

## User problems

1. **No defensible number.** "How good is your agent security?" has no reproducible answer.
2. **Policy changes are unverified.** A rule edit can silently un-block a known attack.
3. **Attacks are point-in-time.** Red-team results go stale the moment config changes.
4. **Vendors over-claim.** Nothing publishes the misses.

## Critical user journeys (v0.1.0)

### CUJ-1 — Run a pack against my deployed stack
1. Ravi selects a pack: `agentdrill run --pack replit-destructive-command --target ./my-stack.yaml --sandbox`.
2. agentdrill delivers the attack through the configured driver and reads the deployed stack's decision.
3. **Success:** a real `blocked` / `missed` / `degraded` result with the agentwatch evidence behind it, in ≤15 minutes from a fresh machine.

### CUJ-2 — Gate a policy PR in CI
1. A contributor edits a compiled rule; CI runs the shipped packs against the candidate stack (`--ci`).
2. A case that must be `blocked` returns `missed`.
3. **Success:** the build fails with the exact pack + case + evidence + exit code; the change cannot merge.

### CUJ-3 — Reproduce a published benchmark result
1. An external engineer clones the release's pack set + `run-manifest.json` (pins, seeds, versions).
2. They re-run against the published pinned config.
3. **Success:** same blocked/missed/degraded numbers as published — including the misses.

### CUJ-4 — Drill a named incident pattern
1. Ravi picks an incident (MCP tool poisoning, Slack-AI exfil, Plugin4Shell supply-chain, credential evasion).
2. Runs the corresponding pack; reviews **step-level** detail (which step succeeded/failed).
3. **Success:** the pack faithfully replays the documented pattern and the oracle decides correctly.

### CUJ-5 — Verify kill-time
1. Ravi runs the kill-time pack; agentdrill drives agenthalt/agentkeys revoke and times to actual cessation.
2. **Success:** a measured latency number published alongside the block/miss result — never inferred.

### CUJ-6 — Run the ecosystem self-attack (evasion) pack
1. On every release cycle, the evasion pack runs attacks on the ecosystem's **own** products (tamper,
   hook-disabling, policy editing, telemetry injection).
2. **Success:** a tamper regression fails loudly; the pack has a per-release cadence.

### CUJ-7 — Contribute or import a pack
1. Alex imports a promptfoo/garak/AgentDojo/PyRIT suite into the pack format and tags it ATLAS/OWASP.
2. **Success (v0.1.0 stub):** import fidelity + first-run success. Full reviewed contribution flow is v1.x (R11).

### CUJ-8 — Close the loop: turn a miss into a policy fix (P2 Ravi)
1. A drill finds a `missed` case; agentdrill emits an **advisory** rule suggestion for agentpolicy/policyweave.
2. Ravi runs a **what-if replay**: the same pack against the candidate policy — *"would this rule have stopped it?"*
3. **Success:** the fix is proposed as a PR a human reviews; the replay proves the rule closes the miss; nothing is auto-applied.

### CUJ-9 — Watch the trend, not the snapshot (P2/P6)
1. Ravi opens the trend view: per-defense-class deltas across releases ("kill-time regressed 400ms since v0.1.2"; "MCP drift coverage improved").
2. **Success:** every published release comparable on the same axes; "what got worse" is one query, with manifests behind it.

### CUJ-10 — Prove coverage, not just results (P2)
1. Ravi runs `agentdrill coverage` — the reconciler maps the agentwatch inventory (tools, MCP servers, capabilities) against the packs.
2. **Success:** every surface is *exercised* or explicitly *declared out of scope*; `gap:unexplained` is zero.

### CUJ-11 — Hand an auditor one finding, verifiable offline (P2)
1. Ravi exports a finding's **evidence bundle** (case + run manifest + agentwatch refs + result).
2. **Success:** a third party verifies the bundle offline, on a different machine, without installing agentdrill — the same trust shape as agentwatch's evidence journey.

### CUJ-12 — Know the moment a change un-blocks something (P1 Maya)
1. A dependency/model/policy/harness config changes; the **trigger watcher** re-runs the affected packs (not the whole suite).
2. **Success:** the affected drill surfaces in the PR/check within CI time budget; drift alerts explain *why* it re-ran.

### CUJ-13 — Dispute a published finding, get an answer (P2/public)
1. An external reviewer disputes a published miss/blocked result; they file a public dispute with their reproduction artifacts.
2. **Success:** adjudication on the record within **14 days** — confirmed, corrected (with a flagged golden-change note), or withdrawn (also on the record). No quiet edits.

### CUJ-14 — Attribute the regression to its cause (P2 Ravi)
1. A case flipped `blocked` → `missed` between releases; Ravi asks *why*.
2. `agentdrill attribute <case>` correlates the flip with the target-config diff, pin change, or adapter change that caused it, and names the stage where the chain broke.
3. **Success:** `attributed_to: <config diff + stage>` on the finding — the fix is actionable, not just "it regressed."

### CUJ-15 — Ship an enforcer without breaking its defense contract (P5 Alex)
1. Alex maintains agentgate; their PR changes tool-trust handling.
2. CI runs agentgate's **defense-contract pack** (the required minimal pack every enforcer ships) against the candidate.
3. **Success:** the contract pack gates the enforcer's own release; a contract regression blocks it exactly like a test failure.

### CUJ-16 — Watch the whole kill chain, not one latency (P2)
1. Ravi reads a case's **kill-chain timeline**: attack-start → detected → decided → halted → revoked → ceased, per stage, with p50/p95.
2. **Success:** "revoked in 2s but the agent kept acting for 11s" is visible — the stage that actually failed is named.

### CUJ-17 — Review the gray area myself (P2/P5)
1. A judge-flagged divergence lands in the **HITL review queue**; Ravi inspects the case, trajectory, and judge rationale locally.
2. **Success:** their reviewed verdict is recorded and becomes seed corpus for a future deterministic oracle — the gray area shrinks every cycle.

### CUJ-18 — Roll the same drill across my fleet (P1/P7)
1. Maya points one pack at 12 deployed stacks (opt-in, self-hosted); the aggregator produces per-stack honest coverage.
2. **Success:** one query answers "which of my stacks is the outlier," with per-stack manifests behind each number.

### CUJ-19 — Prove the attack is even possible (efficacy control) (P2/public)
1. Ravi opens a pack's **efficacy report**: each case run against its *unguarded twin*.
2. **Success:** every enforcement-rate number in the table is backed by a case that demonstrably *succeeds* unguarded; inert attacks are flagged `attack_inert` and excluded from rates — no green number is padded by attacks that were never going to land.

### CUJ-20 — Point at a new incident and get a pack (freshness) (P2)
1. A new agent incident drops publicly. Ravi files it to the intake tracker.
2. **Success:** within 7 days it is assessed — pack draft (scaffolded via the authoring SDK, efficacy-verified, cleanup'd) or an explicit not-applicable with reason. The benchmark never goes stale silently.

### CUJ-21 — Watch a fix hold (P2)
1. A miss is confirmed, fixed, and shipped. Months later something drifts.
2. **Success:** the original case is now a **permanent pinned regression case** — `fix_decay` is caught by the CI gate at the drift PR, with attribution naming what decayed it. Fixes are not done when they ship; they are done when they hold.

### CUJ-22 — Probe the seams between my defenses (P2)
1. Ravi runs the **seam pack**: the attack is blocked by control A, then immediately re-attempted via a different route/tool/transport.
2. **Success:** `seam_gap` findings name *both* controls involved — "gate denies route 1, but the same action rides agentkeys route 2" — the composition gap no per-control test can see.

### CUJ-23 — Verify a release without installing anything (public/auditor)
1. A journalist/auditor downloads a published benchmark release bundle.
2. **Success:** the **standalone verifier** (zero-install, offline) returns three unambiguous verdicts — *intact / complete / honest-shaped* — checking signatures, hashes, manifest, efficacy labels, attestation labels, and statistical shape; on failure it names the first broken link.

### CUJ-24 — First run in 15 minutes (P4/P1)
1. A new user runs `agentdrill quickstart` — the bundled demo stack boots, a mini pack runs.
2. **Success:** they see blocked/missed/kill-time, the honest table, and an exportable bundle in minutes, watermarked `demo — never evidence`; then `agentdrill init` scaffolds wiring their real stack.

### CUJ-25 — Check the instrument before trusting the reading (P2/public)
1. Ravi (or a reviewer) opens the oracle credibility page for a release: per-oracle agreement rates, false-block/miss rates, judge drift status, calibration tier.
2. **Success:** every oracle behind every published number shows its calibration status and version — and a drifted judge is caught by the canary, not by a wrong published number.

### CUJ-26 — Run my oracle against your corpus (P5/researcher)
1. A researcher points their own oracle implementation at the published calibration corpus.
2. **Success:** they get their agreement rates against our labels, offline, comparable to our published numbers — the corpus is a submission surface for better oracles (feeds R11 community flow).

### CUJ-27 — Schedule a drill for a live adversary (P2/P5)
1. A new incident drops publicly and does not map to an existing class (novel vendor, novel vector).
2. **Success:** it enters the intake tracker, is assessed in 7 days, becomes a pack draft via a new template or an explicit N/A with reason — never silently dropped.

## Later journeys (not v0.1.0)

- **Compare two stack versions** — attribute which defense regressed (the predecessor harness candidate-vs-baseline).
- **Diagnose a regression family** — group missed attacks by defense class into a coverage-gap report.
- **Competitor/other-tool benchmark** (R12) — the automated honest-coverage table.
- **Fuzzing class** (R13) — OSS-Fuzz-driven packs for the ecosystem's parsers.

## Success criteria for v0.1.0 users

CUJ-1..7 and the v0.1.0 additions CUJ-19/20/23/24 pass on a clean machine; a security engineer runs a
real attack against their own stack and reads an honest result in ≤15 minutes (CUJ-1, CUJ-24); a policy
PR that un-blocks an attack is rejected by CI (CUJ-2); an external reviewer reproduces the published
benchmark (CUJ-3) and verifies it standalone (CUJ-23); each release publishes kill-time plus the
ecosystem self-attack result (CUJ-5, CUJ-6); every published number is efficacy-backed (CUJ-19); and
new incidents reach pack-or-N/A within 7 days (CUJ-20).
