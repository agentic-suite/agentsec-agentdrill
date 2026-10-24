# PRD 12 — Traceability

**BLUF:** Every v0.1.0 requirement traces to a critical user journey, a work breakdown item, an acceptance
test, and its parity disposition. No requirement is orphaned and no absorbed capability is silently
dropped.

**Status:** Draft — v0.1.0 (2026-10-09) · **Owner:** @deghosal-2026 · **Parent:** agentic-suite #209

## Foundation milestones (M0–M1)

M0–M1 carry no new R-items; they establish the engine and identity every later milestone builds on.

| Milestone | Foundation deliverable | Acceptance test |
|---|---|---|
| M0 | Ported predecessor engine → `agentdrill` (v0.1.0, renamed, provenance recorded) | `tests/test_port_hygiene.py`; full ported suite green |
| M1 | CLI surface + reserved exit codes; fail-closed config; CI quality gate; `doctor` | `tests/test_cli_surface.py`, `tests/test_config.py`, `tests/test_ci_workflow.py`, `tests/test_doctor.py` |


## Requirement → CUJ → WBS → test → parity

| Req | Requirement (short) | CUJ | WBS | Acceptance test | Parity (PRD 10) |
|---|---|---|---|---|---|
| **R1** | Versioned incident-replay packs | CUJ-1, CUJ-4 | M2 | Each pack reproduces its incident pattern | Delivered (pack format absorbed) |
| **R2** | Run vs. deployed stack | CUJ-1 | M5 | Packs exercise the real enforcement path | Delivered (adapter contract absorbed) |
| **R3** | CI gate on policy PRs | CUJ-2 | M11 | An un-blocking change is rejected · `tests/test_m11_exit_codes.py` | Delivered (CI exit codes absorbed) |
| **R4** | Public reproducible benchmark | CUJ-3 | M10 | Third party re-runs → same numbers · `tests/test_m10_benchmark.py` | Delivered (manifest + reporting absorbed) |
| **R5** | Honest reporting (misses) | CUJ-3 | M6, M10 | Published results include misses · `tests/test_m10_honest_report.py` | Delivered (report generation absorbed) |
| **R6** | Determinism (seeds/pins/methodology) | CUJ-3 | M8 | Same env ⇒ same result · `tests/test_m8_{fixtures,manifest,pins,contamination,reproduction}.py` | Delivered (fixtures/manifest absorbed) |
| **R7** | Evasion / self-attack pack | CUJ-6 | M14 | Self-attacks run every release cycle · `tests/test_m14_evasion_pack.py`, `tests/test_m14_cadence.py` | Delivered (adversarial-pack pattern) |
| **R8** | Kill-time verification | CUJ-5, CUJ-16 | M12 | Latency published per release · `tests/test_m12_timing.py` | Delivered (new metric) |
| **R9** | Interop import | CUJ-7 | M17 | promptfoo/garak/AgentDojo/PyRIT import runs · `tests/test_m17_interop.py` | Re-pointed (benchmark connectors) |
| **R10** | ATLAS + OWASP tagging | CUJ-7 | M17 | Every pack/attack tagged · `tests/test_m17_tagging.py` | Delivered (new) |
| **R11** | Community pack flow | CUJ-7 | M16 | Reviewed-like-code contribution lands · `tests/test_m16_contribution.py`, `tests/test_m16_signing.py` | Delivered (plugin/trust absorbed) |
| **R12** | Competitor benchmark | CUJ-7, later | M17 | Automated honest-coverage table · `tests/test_m17_competitor.py` | Waived at v0.1.0 |
| **R13** | Fuzzing class | later | M17, M20 | OSS-Fuzz pack runs | Waived at v0.1.0 |
| **R14** | Attack-chain orchestration (multi-step) | CUJ-16 | M15 | Chain runs step by step; `broke_at` names the break — `tests/test_m15_chains.py`, `tests/test_m15_breakpoint.py` | Delivered (new) |
| **R16** | Attack-mutation engine (bounded) | CUJ-16 | M15 | Adaptive case carries provenance + reviewer; caps enforced; deterministic path — `tests/test_m15_adaptive.py`, `tests/test_m15_adaptive_determinism.py`, `tests/test_m15_review_gate.py` | Delivered (bounded, RK-2/RK-13) |

## CUJ → requirement (reverse)

| CUJ | Serves |
|---|---|
| CUJ-1 Run a pack locally | R1, R2, R5 |
| CUJ-2 Gate a policy PR | R3 |
| CUJ-3 Reproduce published result | R4, R5, R6 |
| CUJ-4 Drill a named incident | R1 |
| CUJ-5 Verify kill-time | R8 |
| CUJ-6 Run evasion pack | R7 |
| CUJ-7 Contribute / import a pack | R9, R10, R11 |
| CUJ-8 Close the loop (miss → advisory fix + what-if) | R17 (F21) |
| CUJ-9 Trend across releases | R4 (F23) |
| CUJ-10 Coverage reconciliation | R4, R5 (F26) |
| CUJ-11 Offline-verifiable finding bundle | R4, R5 (F27) |
| CUJ-12 Trigger-driven re-drill on change | R3, R7 (F22) |
| CUJ-13 Dispute a finding → 14-day adjudication | R5, R21 (F32) |
| CUJ-14 Attribute the regression to its cause | R3, R5 (F38) |
| CUJ-15 Enforcer defense contract gates its own release | R3 (F36) |
| CUJ-16 Kill-chain timeline, not one latency | R8 (F37) |
| CUJ-17 HITL gray-area review → seed corpus | R5 (F44) |
| CUJ-18 Fleet rollup across stacks | R4 (F45) |
| CUJ-19 Efficacy control — prove the attack lands | R5, R33 (F59) |
| CUJ-20 Incident intake → pack within 7 days | R1, R34 (F60) |
| CUJ-21 Fix decay caught at the drift PR | R3, R35 (F61) |
| CUJ-22 Seam gaps name both controls | R2, R36 (F62) |
| CUJ-23 Standalone verify a release bundle | R4, R38 (F64) |
| CUJ-24 Quickstart → first honest result ≤15 min | R2, R40 (F66) |

## Requirement → new trust features (added 2026-10-09)

| Req | Feature | Test |
|---|---|---|
| R19 Statistical rigor | F29 | Automated: a result table with a single-seed number fails the publish check — `tests/test_m10_stats.py` |
| R20 Contamination disclosure | F30 | Probe query per case; flagged cases appear in the table |
| R21 Adjudication | F32 | A filed dispute resolves (confirm/correct-with-note/withdraw) ≤14 days |
| R22 Defense contracts | F36 | A contract regression blocks the enforcer's own release |
| R23 Kill-chain stage timing | F37 | Per-stage timestamps + p50/p95/max published per case — `tests/test_m12_timing.py` |
| R24 Attribution | F38 | `attributed_to` includes the stage/mechanism, never a bare diff — `tests/test_m9_attribution.py` |
| R25 Severity rubric | F41 | Findings carry class × exposure + rationale — `tests/test_m10_severity.py` |
| (preregistration) | F31 | A result-vs-golden change without a re-pin note fails CI — `tests/test_m9_golden.py` |
| (dark holdout) | F33 | Published-green + holdout-red = release-blocking finding — `tests/test_m14_holdout.py` |
| (limitations register) | F34 | Publish gate item 5 |
| (signed provenance) | F35 | Verifier checks signatures on a clean machine |
| R26 Cleanup discipline | F50 | `dirty_target` on cleanup failure; release-blocked — `tests/test_m13_cleanup.py` |
| R27 Utility cost | F51 | Benign twin + utility-under-attack + enforcement rate — `tests/test_m13_utility.py` |
| R28 Telemetry validation | F52 | `telemetry_gap` on blocked-without-event |
| R29 Bootstrap CIs | F55 | Publish check rejects bare percentages — `tests/test_m10_ci.py` |
| R30 Traces per row | F56 | Benchmark cell → trajectory in one hop — `tests/test_m10_traces.py` |
| R31 PR submission | F57 | External submission reproduces via CUJ-3 path — `tests/test_m10_benchmark.py` |
| R32 Heat-map | F53 | Per-release coverage matrix + delta generated in CI — `tests/test_m10_heatmap.py` |

## Decisions → requirements

| Decision | Enables |
|---|---|
| DD-02, DD-02 targets | R1, R2 |
| DD-04, DD-07 oracles | R5, R6 |
| DD-06 honest reporting | R5 |
| DD-10 self-test | R7 |
| DD-15..DD-19 engine/storage | R2, R4, R6 |
| DD-20 untrusted packs | R3, R11 |
| DD-21 tagging | R10 |

## Open WBS items (to be scheduled)

The authoritative work breakdown **now exists**: [docs/wbs/v0.1.0/](../wbs/v0.1.0/wbs-v0.1.0-index.md)
(25 milestones, M0 port → M24 release). This table and the WBS agree; the WBS is the operational source of
truth, this PRD is the requirement-side source of truth.

## Later-PRD traceability additions (R33–R58)

| Req | Feature | Test |
|---|---|---|
| R33 Pack efficacy | F59 | Efficacy run per pack release; inert cases excluded from enforcement rates — `tests/test_m13_efficacy.py`, `tests/test_m13_inert.py` |
| R34 Freshness | F60 | New incident assessed ≤7 days (pack draft or N/A + reason) · `tests/test_m18_intake.py` |
| R35 Fix validation | F61 | `fix_decay` release-blocking; fix case pinned to fix commit · `tests/test_m18_fix.py` |
| R36 Seam probing | F62 | `seam_gap` findings name the controls involved · `tests/test_m18_seams.py` |
| R37 Attestation | F63 | Weakest-link label; `mock` excluded from benchmark · `tests/test_m18_attestation.py` |
| R38 Verifier | F64 | Clean-machine, offline, three-verdict output · `tests/test_m18_verifier.py` |
| R39 Bundle privacy | F65 | Redaction receipts verified in bundles · `tests/test_m18_privacy.py` |
| R40 Quickstart | F66 | ≤15 min to first honest result, demo-watermarked · `tests/test_m18_quickstart.py` |
| R41–R52 Frontier & DX | F67–F78 | See [PRD 22](22-frontier-dx-features.md) §Traceability — pack diff, watch, dry-run, templates, schedules, CI export, assertions, provenance, registry sync, diff-aware, MCP read-only, budget versioning |
| R53–R58 Oracle credibility | F79–F84 | See [PRD 23](23-oracle-credibility.md) §Traceability — versioning, corpus, drift, battery, adjudication, labels |

## CUJ → requirement (final)

| CUJ | Serves |
|---|---|
| CUJ-25 Check the instrument | R53–R58 (F79–F84) |
| CUJ-26 Run my oracle against the corpus | R54 (F80), R11 |
| CUJ-27 Schedule a drill for a live adversary | R1, R34 (F60) |

## World-class gap-closure traceability (added 2026-10-10, PRDs 25–43)

| Req | Feature | PRD | CUJs |
|---|---|---|---|
| R59 Attacker-strength tiers | F85 | [25](25-attacker-strength-and-pressure.md) | CUJ-28 |
| R60 Pressure metrics (`Hold@k`/`ASR@k`) | F86 | [25](25-attacker-strength-and-pressure.md) | CUJ-28, CUJ-29 |
| R61 Independent effect witness | F87 | [26](26-independent-effect-witness.md) | CUJ-30, CUJ-31 |
| R62 Adversary Lab | F88 | [27](27-adversary-lab.md) | CUJ-32, CUJ-33 |
| R63 Effect-based bypass search | F89 | [28](28-policy-bypass-search.md) | CUJ-34, CUJ-35 |
| R64 Defense contract/SDK/kit + Zoo | F90 | [29](29-bring-your-own-defense.md) | CUJ-36, CUJ-37 |
| R65 Neutral head-to-head | F91 | [29](29-bring-your-own-defense.md) | CUJ-36 |
| R66 Trace backtest & shadow | F92 | [30](30-trace-backtest-and-shadow.md) | CUJ-38, CUJ-39 |
| R67 Attack-path graph & blast radius | F93 | [31](31-attack-path-and-blast-radius.md) | CUJ-40, CUJ-41 |
| R68 Incident-to-pack compiler | F94 | [32](32-incident-to-pack-compiler.md) | CUJ-42, CUJ-43 |
| R69 Exposure ledger & waivers | F95 | [33](33-exposure-ledger-and-waivers.md) | CUJ-44, CUJ-45 |
| R70 Drill attestations & deploy gate | F96 | [34](34-drill-attestations-and-deploy-gate.md) | CUJ-46, CUJ-47 |
| R71 Rules of engagement & safe-fire | F97 | [35](35-rules-of-engagement-and-safe-fire.md) | CUJ-48, CUJ-49 |
| R72 Extension detonation lab | F98 | [36](36-extension-detonation-lab.md) | CUJ-50, CUJ-51 |
| R73 Break-It program | F99 | [37](37-break-it-program.md) | CUJ-52, CUJ-53 |
| R74 Security ecosystem integrations | F100 | [38](38-security-ecosystem-integrations.md) | CUJ-54, CUJ-55 |
| R75 Frontier attack classes | F101 | [39](39-frontier-attack-classes.md) | CUJ-56, CUJ-57 |
| R76 Trace explorer | F102 | [40](40-trace-explorer.md) | CUJ-58, CUJ-59 |
| R77 Platform compatibility matrix | F103 | [41](41-platform-compatibility.md) | CUJ-60, CUJ-61 |
| R78 Standards, claims & interop | F104 | [42](42-standards-and-claims.md) | CUJ-62, CUJ-63 |
| R79 Evidence register & method | — | [43](43-evidence-register-and-method.md) | — |

> These additions are **v0.1.0 scope**. WBS scheduling (a milestone per feature group) and acceptance
> tests are to be added when the WBS is extended; PRD 43 §PRD-tensions lists the decisions still open.
