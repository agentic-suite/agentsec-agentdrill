# PRD 05 — What (Features)

**BLUF:** agentdrill v0.1.0 is the proof foundation: curated versioned **incident-replay attack packs**
run against the **deployed stack** in **CI**, with **reproducible honest results** (misses included) and
**kill-time** verification — plus an **evasion pack** that attacks the ecosystem itself. It absorbs the
harness mechanics of **the predecessor harness** (pack format, adapter contract, runner, deterministic + judge
scoring, fixtures, baselines/comparison, CI exit codes, sandbox/trust model) and re-points them at
defenses.

**Status:** Draft — v0.1.0 (2026-10-09) · **Owner:** @deghosal-2026 · **Parent:** agentic-suite #209

## v0.1.0 scope

Curated incident-replay packs (R1) run against the deployed stack (R2), gating policy PRs in CI (R3), with
a public reproducible benchmark (R4), honest reporting (R5), determinism (R6), an evasion pack (R7), and
kill-time verification (R8). Local-first, CI-second. ≥2 Tier-1 harnesses at v0.1.0.

## P0 — Must have (v0.1.0)

| # | Requirement | Acceptance criterion |
|---|---|---|
| **R1** | Curated, versioned **incident-replay packs**: Replit destructive-command, Invariant tool-poisoning/shadowing/rug-pull, Plugin4Shell-style supply-chain, Slack-AI-style exfil chain, credential-evasion | Each pack reproduces its documented incident pattern in a demo environment |
| **R2** | Run packs against the **deployed stack** (agentgate, agentkeys, agentseatbelt/agentkernel, policyweave output) — not a simulation | Packs exercise the real enforcement path end-to-end |
| **R3** | **CI-native** pass/fail gates on policy PRs — a change that un-blocks an attack is rejected | Demonstrated in the ecosystem's own CI (dogfooded from Wave 0) |
| **R4** | **Public results**: reproducible benchmark of shipped packs vs. shipped defenses, published per release | A third party re-runs and gets the same numbers |
| **R5** | **Honest-reporting format**: what was blocked, what was **not** caught, what degraded — no scoring theater | Every published result includes the misses |
| **R6** | **Determinism**: pinned seeds, pinned models, documented methodology | Same environment ⇒ same result |
| **R7** | **Evasion pack**: attacks on the ecosystem itself — tamper, hook-disabling, policy editing, injection into telemetry | Ecosystem self-attacks run every release cycle |
| **R8** | **Kill-time verification**: measures agenthalt/agentkeys revocation latency, not just detection | Latency numbers published with each release |

## P1 — Should have (v0.1.0)

- **R9** Import interop: load promptfoo / garak / AgentDojo / PyRIT suites (don't reinvent).
- **R10** Framework/standards tagging: every pack/attack mapped to OWASP LLM Top-10, OWASP Agentic drafts, MITRE ATLAS.
- **R11** Community pack contribution flow (reviewed like code — packs are executable security claims).
- **R14** **Attack-chain orchestration:** multi-step/multi-turn documented chains (F18) as a pack structure, not just single-shot cases.
- **R15** **MCP attack-surface pack class** (F19) and **memory/multi-agent abuse class** (F20).

## P2 — Nice to have

- **R12** Continuous public benchmark of *competitor/other* tools (the honest-coverage table automated).
- **R13** Fuzzing integration for the ecosystem's parsers (OSS-Fuzz as a pack class).
- **R16** **Attack-mutation engine** (F17): bounded synthetic variants of documented patterns — mutation only, no novel capability (see [PRD 08](08-risks.md) dual-use line).
- **R17** **Closes-the-loop policy suggestion** (F21): advisory rule + what-if replay from a confirmed miss.
- **R18** **Compliance-mapped reporting** (F24): EU AI Act / NIST AI RMF / ISO 42001 evidence export (via agentcomply).
- **R19** **Statistical rigor** (F29): multi-seed mean ± std, CIs on judge metrics, percentiles on kill-time — no single-run claims in any published table.
- **R20** **Contamination disclosure** (F30): pack cases flagged when they overlap judge/target-model training data; contaminated cases marked, never silently dropped.
- **R21** **Adjudication** (F32): independent-reviewer validation + a public dispute process with a resolution SLA on every published finding.
- **R22** **Defense contracts** (F36): every ecosystem enforcer ships a required minimal pack that gates its own release.
- **R23** **Kill-chain stage timing** (F37): per-case stage timestamps across the full chain, published as a timeline.
- **R24** **Attribution** (F38): a blocked→missed flip is attributed to the specific config/pin diff that caused it.
- **R25** **Severity rubric** (F41): findings carry attack-class × exposure severity with rationale.
- **R26–R32** **Detection-validation & BAS-class features** (F49–F58): cleanup discipline, utility-under-attack,
  expected-telemetry validation, coverage heat-maps, adversary profiles, bootstrap CIs, per-row traces,
  PR-based benchmark submission, multi-format reports — see [PRD 19](19-detection-validation-bas.md).

## Feature catalog (v0.1.0)

| # | Feature | Requirement | Absorbed from the predecessor harness |
|---|---|---|---|
| F1 | Attack-pack format + catalog (versioned YAML) | R1 | Scenario pack format + launch/security packs |
| F2 | Runner (`run_one`/`run_all`, per-case timeout/isolation, continue-on-failure) | R2 | Core runner |
| F3 | Driver + target adapter contract (invocation payload, run envelope, no ground-truth leakage) | R2 | Adapter contract (subprocess/python/HTTP + frameworks) |
| F4 | Deterministic + judge oracle engine, three dimensions, honest outcome split | R5 | Deterministic (17) + judge (11) + hybrid scoring |
| F5 | Fixtures / ToolStub determinism (record + replay, `--live`) | R6 | Fixture system + ToolStub |
| F6 | Reproducible run manifest + pins | R6 | `run-manifest.json` |
| F7 | Golden expected results + coverage/regression comparison (adapter/model-change detection) | R4 | Baseline + comparison engine |
| F8 | Honest reporter (JSON/Markdown/GitHub-Actions) + public benchmark publisher | R5, R4 | Report generation + failure taxonomy |
| F9 | CI surface (exit codes, `--ci`, `$GITHUB_STEP_SUMMARY`, `--fail-on`) | R3 | CI integration + exit codes |
| F10 | Kill-time probe (drive agenthalt/agentkeys revoke; measure cessation) | R8 | (new — measures latency, not detection) |
| F11 | Evasion/self-attack pack (tamper, hook-disable, policy-edit, telemetry-injection) | R7 | Adversarial pack pattern |
| F12 | Interop importer (promptfoo/garak/AgentDojo/PyRIT) | R9 | Benchmark/connector architecture |
| F13 | Standards tagger (ATLAS + OWASP) | R10 | (new) |
| F14 | Plugin registry (custom oracles/adapters) + trust levels (`built-in`/`local`/`external`) | R11 | Plugin registry + trust policies |
| F15 | Security model for untrusted packs (sandbox, trust, audit trail, secret sanitization) | R3, R11 | Sandbox + audit + sanitization |
| F16 | Live benchmark results site/table (per release, with misses) | R4 | (new) |
| F17 | **Attack-mutation engine** — synthetic variants of documented patterns (argument fuzzing, encoding/payload perturbation, paraphrase mutation) | R1, R6 | the predecessor harness synthetic adversarial case generation (fuzzer + security evals) |
| F18 | **Attack-chain orchestration** — multi-step/multi-turn chains (recon → injection → tool misuse → exfil → cover-up) as first-class pack structure | R1 | PyRIT-style multi-turn orchestration, replaying documented chains (Slack-AI exfil, Replit) |
| F19 | **MCP attack-surface pack class** — tool-surface drift/rug-pull, schema/description poisoning, cross-server shadowing, WhatsApp-style agent weaponization, driven via agentgate | R1, R2 | (new — Invariant-documented MCP attacks) |
| F20 | **Memory & multi-agent abuse pack class** — memory poisoning/stale-context carryover, cross-task leakage, multi-agent chaining/delegation abuse | R1 | (new — OWASP Agentic + 2026 tool coverage) |
| F21 | **Closes-the-loop policy fix** — a confirmed miss generates an advisory rule suggestion + what-if replay against agentpolicy/policyweave (never auto-applied) | R3 | Straiker Ascend→Defend pattern; the predecessor harness what-if posture |
| F22 | **Trigger-driven continuous drilling (CART)** — packs re-run on policy/model/config/harness change (not just scheduled), with drift alerts feeding the trigger | R3, R7 | Continuous Automated Red Teaming posture |
| F23 | **Trend analytics** — vulnerability trends across releases (per-defense-class deltas, "what got worse since v0.1.2"), benchmark history store | R4 | Leaderboard trend tracking (promptfoo enterprise pattern) |
| F24 | **Severity ratings + compliance-mapped reporting** — findings carry severity; reports map to OWASP LLM + Agentic, MITRE ATLAS, NIST AI RMF, EU AI Act Art. 12; evidence exportable to agentcomply | R10 | OWASP/NIST/EU mapping (DeepTeam/Straiker pattern) |
| F25 | **Kill-chain mapping** — every pack mapped to attack stages; per-stage control verification shows *where* the chain was broken | R5 | (new — makes misses diagnosable, not just counted) |
| F26 | **Coverage reconciliation** — consume agentwatch inventory (tools, MCP servers, capabilities) and report which surfaces the packs exercised vs. missed | R4, R5 | agentwatch coverage discipline (gap:unexplained = zero) |
| F27 | **Evidence bundle per finding** — a third party verifies a single finding offline (pack case + manifest + agentwatch evidence refs) | R4, R5 | agentwatch CUJ-8 evidence-bundle pattern |
| F28 | **Standards participation surface** — submit packs/results to NIST CAISI (AgentDojo-Inspect interop) and OWASP Agentic; import community findings | R4, R9 | NIST CAISI 2026 program; AgentDojo-Inspect |
| **— Trustworthiness & statistical rigor (the benchmark-trust layer)** | | | |
| F29 | **Multi-seed statistical rigor** — every published number is mean ± std over ≥3 pinned seeds; a single run is never a claim; judge metrics report CIs; kill-time reports percentiles (p50/p95), not just means | R5, R6 | (new — anti-"three numbers to lie") |
| F30 | **Contamination check** — detect when a pack case's content overlaps a judge/target model's training data (memorized answers ≠ measured defenses); flag contaminated cases in results | R6 | LiveCodeBench/SWE-Bench contamination posture |
| F31 | **Preregistration + golden locks** — expected outcomes are preregistered per pack version; a result that changed vs. its golden is *flagged*, never silently updated; changes require a re-pin note | R4, R6 | (new — preregistration discipline) |
| F32 | **Adversarial adjudication** — independent-reviewer authorship for pack validation (the JPS pattern); a public dispute process on published findings with a resolution SLA | R4, R5 | JPS hidden-adversarial-case pattern |
| F33 | **Dark holdout** — a private (unpublished) holdout subset of each pack runs in CI to detect pack-gaming / overfitting-to-the-published-set; only aggregate pass/fail is published | R4, R7 | HLE "dark benchmark" pattern |
| F34 | **Limitations register** — every release ships an explicit, honest known-limitations list (what these packs do NOT test, where coverage is thin); never claims more than was measured | R5 | agentwatch known-limitations discipline |
| F35 | **Provenance + signature on every published artifact** — packs, manifests, results, and bundles are signed (Sigstore) with full provenance; a third party can verify authenticity, not just re-run | R4, R6 | SLSA/signature posture |
| **— World-class additions (researched 2026-10-09)** | | | |
| F36 | **Defense contracts** — every ecosystem enforcer (agentgate, agentkeys, agentseatbelt/kernel, policyweave, agenthalt) ships a **required minimal pack** as part of its own release gate; its release is blocked if its contract pack regresses | R3, R7 | Formalizes the dogfood requirement (ecosystem R3 "demonstrated in our own CI") |
| F37 | **Full kill-chain timing** — beyond revocation latency: stage timestamps for the whole chain (attack-start → detected → decided → halted → revoked → ceased), per case; publishes a **kill-chain timeline**, not one latency number | R8 | Extension of R8 (means hide tails; chains hide stages) |
| F38 | **Regression attribution** — when a case flips blocked→missed, attribute the flip to the specific target-config/diff/pin that caused it (config diff × pack case × stage), so the fix is actionable | R3, R5 | Detective-work extension; the predecessor harness trace-diff + adapter/model-change detection pattern |
| F39 | **Pack registry + pack governance** — semver'd packs with changelog, deprecation policy, signing, registry index; `agentdrill pack publish/verify/deprecate`; migration notes on format evolution | R11, R9 | promptfoo/garak community-suite governance patterns |
| F40 | **Bounded adaptive orchestration** — a PyRIT-style attacker step that mutates a *documented* pattern based on target responses, hard-capped by the dual-use boundary (mutation-of-documented-patterns only, no novel capability), always labeled `adaptive` in results | R1, R6 (dual-use: PRD 08) | PyRIT orchestrator pattern, inside the RK-2 boundary |
| F41 | **Severity rubric** — misses scored attack-class × exposure (à la CVSS-for-agent-defense): a finding carries severity + rationale, sortable across packs; feeds prioritization and the trend store | R5 | Straiker/severity-rating pattern |
| F42 | **Recon/scoping phase** — before running cases, probe the target stack's exposed surface (tools, MCP servers, capabilities via agentwatch inventory) and **bind cases to what exists**; a case that references a nonexistent surface fails loudly, not silently | R2, R4 | Recon-then-attack red-team flow; agentwatch inventory interop |
| F43 | **Drill-the-drill (meta-verification)** — adversarial cases against agentdrill's *own* oracle engine (can a target/harness fool the scorer? forge evidence? bluff the judge?), run in CI beside the evasion pack | R7 | JPS independent-reviewer pattern applied to our own oracles |
| F44 | **HITL review queue** — judge-flagged divergences and uncertain outcomes land in a human review queue (CLI + file-based, local-first), and reviewed verdicts become **seed corpus** for future deterministic oracles | R5 | Evaluation-stratification best practice (auto → judge → human expert) |
| F45 | **Fleet mode** — run the same pack across many deployed stacks (opt-in, self-hosted), aggregate honest coverage across the fleet with per-stack breakdowns and per-release comparability | R4 | Fleet rollup pattern (agentwatch fleet views; enterprise CART) |
| F46 | **Authoring SDK + scaffolding** — `agentdrill init` (pack scaffold + CI workflow), a pytest-style Python API for authoring cases, pack lint (schema + tag + path-safety + method checks), and per-case fixtures recording | R11 | the predecessor harness `init` + pytest-plugin + scaffold patterns |
| F47 | **PR annotations + regression alerts** — a regressed case posts a PR annotation naming the case, stage, evidence ref, and attribution; Slack/webhook alert on release-gate failure | R3 | promptfoo/agentwatch CI annotation patterns |
| F48 | **IR replay** — replay any case (or finding) step-by-step as an incident-response artifact: what was attempted, what the stack did at each stage, where the chain broke — handable to a third party with the evidence bundle (F27) | R4, R5 | agentwatch replay-as-evidence pattern |
| **— Detection-validation & BAS-class features (PRD 19)** | | | |
| F49 | **Plugin discovery** — `agentdrill list` packs/oracles/targets/drivers + `plugin info` (garak `--list_probes` pattern) | R9, R11 | garak plugin architecture |
| F50 | **Per-case cleanup** — every case declares cleanup; cleanup failure = release-blocking `dirty_target` finding (a dirty target invalidates all later numbers) | R6 | Caldera cleanup functions / ART cleanup commands |
| F51 | **Utility-under-attack** — every attack case carries a benign twin; publish benign utility + utility-under-attack + enforcement rate; `utility_cost` findings | R5 | AgentDojo three-metric frame |
| F52 | **Expected-telemetry validation** — cases declare the agentwatch events a true block must produce; blocked-without-telemetry = `telemetry_gap` finding | R2, R5 | BAS expected-telemetry pattern |
| F53 | **Coverage heat-map** — pack/tag × control matrix (`blocked/partial/missed/untested`) per release + delta | R4 | AT&CK-nav / BAS posture scorecard |
| F54 | **Adversary profiles** — pack-level threat-intel card (who, what, source, objective) | R10 | Caldera adversary profiles |
| F55 | **Bootstrap CIs on outcome rates** — `blocked 87% [81%, 92%] (n, seeds)`, never a bare percentage | R19 | garak v0.14.1 bootstrap ASR CIs |
| F56 | **Traces per published row** — every benchmark cell links full trajectory + evidence in one hop | R4 | AgentDojo leaderboard trace discipline |
| F57 | **PR-based benchmark submission** — fork → run pinned packs → PR results; the R12 enabler | R12 | AgentDojo PR submission flow |
| F58 | **Multi-format operation reports** — JSON / Markdown / self-contained HTML (offline) / PDF | R24 | Caldera operation reports |
| **— Efficacy, freshness & lifecycle (PRD 20)** | | | |
| F59 | **Pack efficacy control** — every pack runs its cases against an *unguarded* twin; only efficacy-verified cases count (inert attacks flagged `attack_inert`, excluded from enforcement rates, never pad a green table) | R5, R6 | The control group no agent benchmark runs (SWE-Bench flawed-tests lesson) |
| F60 | **Incident-intake pipeline** — watchlist → 7-day triage SLA → pack draft → review → registry; deprecation of stale packs | R1 | LiveCodeBench freshness discipline |
| F61 | **Remediation validation** — every fixed miss becomes a permanent pinned regression case; `fix_decay` is release-blocking | R3 | Straiker "validates fixes hold" pattern |
| F62 | **Cross-defense seam probing** — denied-then-retried cases + multi-enforcer composition cases; `seam_gap` findings | R2 | agentwatch denied-then-retried; composition-gap reality |
| F63 | **Target attestation** — `live`/`fixture`/`mock` declared per component; results labeled at the weakest link; `mock` never publishes | R5 | Closes the "deployed stack" honesty gap (RK-6) |
| F64 | **Standalone verifier** — zero-install, offline verification of bundles/releases: signatures, hashes, manifest, labels, statistical shape; three verdicts | R4 | agentwatch verifier pattern |
| F65 | **Evidence privacy** — redaction-before-bundling with receipts (what class, how many, where); verifier checks receipts | R4, R5 | agentwatch redaction-receipt pattern |
| **— Frontier & DX features (PRD 22)** | | | |
| F67 | **Pack diffing & selection** — `agentdrill pack diff <a> <b>` (case-level + coverage delta) and `agentdrill list cases --tag/--target/--difficulty` for targeted re-runs | R1, R3 | pytest `--collect-only` + garak probe-selection patterns |
| F68 | **Watch mode** — `agentdrill watch` re-runs affected packs on file/config/harness change (the interactive CART loop for local dev, not just CI) | R3 | watchexec/pytest-watch pattern, applied to target drift |
| F69 | **Dry-run & explain plan** — `agentdrill run --dry-run` prints the bound cases, targets, oracle verdicts-expected, and evidence expectations without executing; `--explain` annotates why each case exists | R2 | pre-flight validation pattern; NIST "explain the plan" evaluation DX |
| F70 | **Pack template library** — `agentdrill init --template mcp-poisoning|exfil-chain|destructive-command|supply-chain` scaffolds a pack from a documented incident class with oracle stubs, twins, cleanup | R11 | cookiecutter/pytest-template patterns |
| F71 | **Scheduled drills (cron-mode)** — `agentdrill schedule` runs pack sets on a cadence and files findings as issues/PRs; handles attack surfaces that change outside code-PR flow (SaaS model updates, MCP server drift) | R3, R22 | CART continuous-cadence posture |
| F72 | **Export CI matrices** — one-command export of the pack set + manifest + attestation as a GitHub Actions / GitLab CI matrix config, so a new stack is "add one row" | R3 | promptfoo/CI template patterns |
| F73 | **Programmatic assertions** — a Python API (`assert_blocked(case_id)`, `assert_missed()`, `assert_kill_time_under(x)`) for teams embedding drills directly in their own test suites | R3 | pytest-fixture-assertion pattern |
| F74 | **Pack provenance cards** — machine-readable card per pack: sources, dates, mutation policy, author, reviews — displayed on every result so a table cell can be traced to *people*, not just commits | R5 | Model-card discipline |
| F75 | **Public registry feed** — `agentdrill registry sync` fetches the signed public pack index (read-only), so a fresh install can pull the ecosystem's pack set without vendoring | R11 | pip-style index semantics, signature-verified |
| F76 | **Diff-aware re-runs** — when a target changes, only the cases bound to the changed surface re-run (per-case `attributed_to` drives selection); CI time scales with diff size, not pack size | R3, R24 | test-selection (pytest-testmon) pattern |
| F77 | **MCP server as a drill surface** — expose pack/run/result queries over a read-only MCP server so coding agents can ask "what regressed?" mid-session without leaving the loop | R2 | agentwatch read-only MCP pattern |
| F78 | **Kill-time budgets in policy** — publish per-case kill-time budgets (`max_seconds`) alongside enforcement rules in policyweave output, so the *budget* is versioned and drilled like the rule | R8 | extension of F37/F18 |
| F66 | **Demo stack + quickstart** — `agentdrill quickstart` boots a bundled demo target and produces a first honest result in minutes; demo watermarked `never evidence` | R2 | agentwatch demo-bundle + ≤15-min discipline |

### P2 additions (from PRD 22 — see the full table there)

- **R41–R52** **Frontier & DX features** (F67–F78): pack selection/diff, watch mode, dry-run/explain,
  templates, scheduled drills, CI-matrix export, programmatic assertions, provenance cards, registry
  sync, diff-aware re-runs, read-only MCP drill surface, versioned kill-time budgets — full definitions,
  tests, and sequencing in [PRD 22](22-frontier-dx-features.md).

## v0.1.0 additions (PRD 25–43) — world-class gap closure

Researched 2026-10-10 against 2025–26 evidence, standards, commercial BAS/AI-red-team products and
best-in-class OSS (see [PRD 43](43-evidence-register-and-method.md)). Priority: **P0** = adoption-blocking
or credibility-defining.

| # | Requirement | PRD | Pri |
|---|---|---|---|
| **R59–R60** | Attacker-strength tiers + `Hold@k`/pressure curves | [25](25-attacker-strength-and-pressure.md) | P0 |
| **R61** | Independent effect witness (defense-vs-witness verdict) | [26](26-independent-effect-witness.md) | P0 |
| **R62** | Adversary Lab (hostile counterparties) | [27](27-adversary-lab.md) | P1 |
| **R63** | Effect-based policy bypass search | [28](28-policy-bypass-search.md) | P0 |
| **R64–R65** | BYOD contract/SDK/kit + neutral head-to-head | [29](29-bring-your-own-defense.md) | P0 |
| **R66** | Trace backtest & shadow mode (false-block budget) | [30](30-trace-backtest-and-shadow.md) | P0 |
| **R67** | Attack-path graph & blast radius | [31](31-attack-path-and-blast-radius.md) | P1 |
| **R68** | Incident-to-pack compiler & threat feed | [32](32-incident-to-pack-compiler.md) | P1 |
| **R69** | Exposure ledger & time-boxed waivers | [33](33-exposure-ledger-and-waivers.md) | P0 |
| **R70** | Drill attestations & deploy gate | [34](34-drill-attestations-and-deploy-gate.md) | P1 |
| **R71** | Rules of engagement & safe-fire interlocks | [35](35-rules-of-engagement-and-safe-fire.md) | P0 |
| **R72** | Extension detonation lab | [36](36-extension-detonation-lab.md) | P1 |
| **R73** | Break-It program (crowd bypass intake) | [37](37-break-it-program.md) | P2 |
| **R74** | Security ecosystem integrations (SARIF/OTel/OCSF/OSCAL…) | [38](38-security-ecosystem-integrations.md) | P0 |
| **R75** | Frontier attack classes (ASI coverage) | [39](39-frontier-attack-classes.md) | P1 |
| **R76** | Trace explorer | [40](40-trace-explorer.md) | P1 |
| **R77** | Platform compatibility & support matrix (L0–L4) | [41](41-platform-compatibility.md) | P0 |
| **R78** | Standards, claims & interop (vocabulary + linter) | [42](42-standards-and-claims.md) | P1 |
| **R79** | Evidence register & method (research base) | [43](43-evidence-register-and-method.md) | — |

Features **F85–F104**; CUJs **CUJ-28–CUJ-63** (see [PRD 12](12-traceability.md)).

## Compatibility (harness-agnostic or explicitly compatible)

> **Non-negotiable:** agentdrill is agentic-harness-agnostic or explicitly harness-compatible. It works
> across harnesses by construction where it targets a protocol/kernel/credential layer, or ships **named
> per-harness attack packs** with a published compatibility table.

| Tier | Harness | v0.1.0 requirement |
|---|---|---|
| 1 — Coding agents | Claude Code · Cursor · GitHub Copilot · Codex CLI · Gemini CLI | **≥2 at v0.1.0**; all 5 target (or documented lower-layer coverage) in v0.1.0 |
| 2 — Frameworks | LangGraph · CrewAI · OpenAI Agents SDK · AutoGen/AG2 · LlamaIndex · PydanticAI · smolagents | **≥3 adapters targeted**; v0.1.0 covered via promptfoo/garak interop |
| 3 — Protocol/enterprise | Generic MCP clients · enterprise platforms | MCP-layer coverage via agentgate; enterprise via standards at v2.x |

A harness is "compatible" only when **its pack passes in CI**; release notes carry the compatibility table.

## Explicit non-requirements

- **No injection-detection claims** from drill results — we measure our enforcement controls, never market "injection solved."
- **No model-attacking capability development** — we replay documented patterns; not a red-team arsenal.
- **No proprietary scoring** — public methodology or nothing.
- **No enforcement** — agentdrill composes the enforcers; it never becomes one.

## Standards it must meet

promptfoo/garak/AgentDojo/PyRIT interop (import, not replace); MITRE ATLAS + OWASP tagging on every pack;
reproducibility (seeds, pins, published methodology); results in the **agentwatch schema** where
machine-consumed.

## Fit in the ecosystem

The proof layer. It drives adoption of every other tool (a drill needs a target), feeds results into
agentwatch, and doubles as the release gate for the ecosystem's own rule packs. Dependency position:
*agentdrill ⟵ any enforcer + watch* — it needs **targets**, ships early, and grows.

## Success metrics (outcome-level)

- Third-party reproduction of published results (≥1 verified external run per release).
- Misses found by users and added to the public table within a week.
- Community pack contributions (health).
- External tools submitting to the benchmark (the convention-winning signal).
