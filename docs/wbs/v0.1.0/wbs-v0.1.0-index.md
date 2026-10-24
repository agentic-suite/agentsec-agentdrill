# WBS — agentdrill v0.1.0 (Index)

**BLUF:** **M0 is a bulk port of the entire predecessor eval-harness codebase** (urgent — it makes
agentdrill self-contained; the predecessor repo is retained and made private, never deleted). After the
port, v0.1.0 delivers the **entire PRD scope** — the proof engine (attack packs, runner, driver/target
adapters, oracle engine, evidence, honest benchmark), the trust layer (efficacy control, kill-chain
verification, oracle credibility), the BAS/detection-validation features, chains + bounded adaptive
orchestration, the pack registry, interop + standards, the lifecycle features, and the **world-class
gap-closure additions** (PRDs 25–43: effect witness, pressure curves, bypass search, BYOD, backtest,
attack-path, exposure ledger, attestations, rules-of-engagement, detonation, frontier classes, explorer,
platform matrix, standards/claims). **Thirty-three milestones (M0–M32)** across **seventeen detail files**;
**field tests (M31) and release readiness (M32) are last.**

## Standard milestone exit criteria (applies to EVERY milestone)

- [ ] **All tests pass** (`make test`) — the milestone's `.T` work item
- [ ] **Code coverage ≥ 95%** (enforced in CI) — the `.C` work item
- [ ] **Lint strict clean** — `ruff` zero violations; `mypy --strict` clean — the `.L` work item
- [ ] **Code review complete** — findings recorded in [codereview-log.md](codereview-log.md), all resolved — the `.CR` work item
- [ ] **Design docs updated** (milestone-specific list in each file) — the `.D` work item
- [ ] **Traceability updated** — the [PRD 12](../../prd/12-traceability.md) requirement → test row moves with the work
- [ ] **Port / absorption / gap items complete** — each milestone frontloads its predecessor-port tasks and its [PRD 24](../../prd/24-predecessor-gap-closure.md) items

> Every milestone therefore carries five standing gate work items — **`.T` tests · `.C` coverage · `.L` lint/types ·
> `.CR` code review · `.D` docs** — in addition to its implementation items.

## Standard milestone closure (applies to EVERY milestone)

A milestone is **closed** only when all of these hold (mirrors agentwatch's closure model + the org
definition of done):

1. **Implemented** — every work item done; no "core slice", no partials.
2. **Tests green** — the milestone's tests pass, and the standard gates run **once at milestone end**
   (full suite, coverage ≥95%, `ruff`, `mypy --strict`) — not per ticket.
3. **Committed & pushed** — the work is on the feature branch, pushed.
4. **Tracking issue closed** — or explicitly commented with status.
5. **Docs updated** — the milestone's design/reference docs updated and linked from this WBS.
6. **Checkpoint recorded** — a dated line appended to the Progress section below (commit refs + gate result).
7. **Field tests (M31) and release readiness (M32) are the final milestones** — **M32 tags `v0.1.0`**.

> **One ticket at a time:** per work item, write the test first (RED) → implement (GREEN) → next. Do **not**
> run the full suite between tickets; run it at milestone end only.

## Milestones

| M | Name | Detail file |
|---|---|---|
| **M0** | **Port the predecessor codebase** (urgent) | [Part 1](wbs-v0.1.0-part1-port-foundation.md) |
| M1 | Foundation & identity | [Part 1](wbs-v0.1.0-part1-port-foundation.md) |
| M2 | Pack format, loader & validation | [Part 2](wbs-v0.1.0-part2-packs-runner.md) |
| M3 | Runner & execution spine | [Part 2](wbs-v0.1.0-part2-packs-runner.md) |
| M4 | Driver adapters | [Part 3](wbs-v0.1.0-part3-drivers-targets.md) |
| M5 | Target adapters & recon/scoping | [Part 3](wbs-v0.1.0-part3-drivers-targets.md) |
| M6 | Oracle engine | [Part 4](wbs-v0.1.0-part4-oracles-evidence.md) |
| M7 | Evidence integration | [Part 4](wbs-v0.1.0-part4-oracles-evidence.md) |
| M8 | Determinism — fixtures, manifest & pins | [Part 5](wbs-v0.1.0-part5-determinism-comparison.md) |
| M9 | Golden results, comparison & attribution | [Part 5](wbs-v0.1.0-part5-determinism-comparison.md) |
| M10 | Honest reporter & public benchmark | [Part 6](wbs-v0.1.0-part6-benchmark-ci.md) |
| M11 | CI gate, trigger/CART & local loop | [Part 6](wbs-v0.1.0-part6-benchmark-ci.md) |
| M12 | Kill-time & kill-chain verification | [Part 7](wbs-v0.1.0-part7-killchain-efficacy.md) |
| M13 | Efficacy control & utility-under-attack | [Part 7](wbs-v0.1.0-part7-killchain-efficacy.md) |
| M14 | Evasion pack & drill-the-drill | [Part 8](wbs-v0.1.0-part8-evasion-chains.md) |
| M15 | Attack chains & bounded adaptive orchestration | [Part 8](wbs-v0.1.0-part8-evasion-chains.md) |
| M16 | Pack registry, signing & governance | [Part 9](wbs-v0.1.0-part9-registry-interop.md) |
| M17 | Interop, standards tagging & compliance | [Part 9](wbs-v0.1.0-part9-registry-interop.md) |
| M18 | Lifecycle — intake, fix-validation, seams, attestation, verifier, quickstart | [Part 10](wbs-v0.1.0-part10-lifecycle-oracle.md) |
| M19 | Oracle credibility | [Part 10](wbs-v0.1.0-part10-lifecycle-oracle.md) |
| M20 | Frontier & DX | [Part 11](wbs-v0.1.0-part11-dx-absorption.md) |
| M21 | Predecessor absorption & gap closure | [Part 11](wbs-v0.1.0-part11-dx-absorption.md) |
| M22 | NFRs, security hardening & resilience | [Part 12](wbs-v0.1.0-part12-hardening-fieldtest.md) |
| **M23** | **Independent effect witness & adversary lab** (additions) | [Part 13](wbs-v0.1.0-part13-effect-witness-bypass.md) |
| **M24** | **Attacker strength, pressure & bypass search** (additions) | [Part 13](wbs-v0.1.0-part13-effect-witness-bypass.md) |
| **M25** | **Bring-your-own-defense & neutral head-to-head** (additions) | [Part 14](wbs-v0.1.0-part14-byod-integrations.md) |
| **M26** | **Security ecosystem integrations** (additions) | [Part 14](wbs-v0.1.0-part14-byod-integrations.md) |
| **M27** | **Backtest, attack-path & incident intake** (additions) | [Part 15](wbs-v0.1.0-part15-context-governance.md) |
| **M28** | **Exposure ledger, attestations & rules of engagement** (additions) | [Part 15](wbs-v0.1.0-part15-context-governance.md) |
| **M29** | **Detonation, Break-It & frontier attack classes** (additions) | [Part 16](wbs-v0.1.0-part16-frontier-platform-standards.md) |
| **M30** | **Trace explorer, platform matrix & standards** (additions) | [Part 16](wbs-v0.1.0-part16-frontier-platform-standards.md) |
| **M31** | **Field tests** (last) | [Part 17](wbs-v0.1.0-part17-fieldtest-release.md) |
| **M32** | **Release readiness** (last; tags `v0.1.0`) | [Part 17](wbs-v0.1.0-part17-fieldtest-release.md) |

## Issues & milestones (GitHub)

The v0.1.0 additions ship as **GitHub issues** under milestones `0.1.0 — M<n> <name>` (labels `0.1.0`, `wbs`),
one per work item. Body standard: Why · Behavior/What · How · Data & schema impact · Security & privacy ·
Edge cases · Testing · Risks & mitigations · Acceptance criteria · Dependencies · References · Definition of
done; marker `<!-- wbs:<item_id> -->`. The **Issue** column in each part file holds the live number; update
them with [`scripts/wbs_issues.py`](../../../scripts/wbs_issues.py).

| M | Milestone | Issues | M | Milestone | Issues |
|---|---|---|---|---|---|
| M23 | Independent effect witness & adversary lab | #288–#300 | M28 | Exposure ledger, attestations & RoE | #347–#358 |
| M24 | Attacker strength, pressure & bypass search | #301–#313 | M29 | Detonation, Break-It & frontier classes | #359–#370 |
| M25 | BYOD & neutral head-to-head | #314–#323 | M30 | Trace explorer, platform matrix & standards | #371–#382 |
| M26 | Security ecosystem integrations | #324–#335 | M31 | Field tests | #82–#91, #383 |
| M27 | Backtest, attack-path & incident intake | #336–#346 | M32 | Release readiness | #92–#105 |

**120 work-item issues total.** M31/M32 reuse the existing field-test/release issues (#82–#105), repurposed
in place; the extra field-test item is #383. Existing milestones M0–M22 keep their issues.

## Progress

**🚧 M27–M32 not started; ✅ M0–M26 complete.** Design complete ([PRD 00–43](../../prd/README.md)). As milestones
close, dated checkpoints (commit refs + gate result) are appended here — matching agentwatch's
per-milestone checkpoints.

- **M0 — Port the predecessor codebase — ✅ 2026-10-10.** Imported the predecessor eval harness (MIT) and
  renamed to `agentdrill`; version reset to **0.1.0**; provenance recorded; predecessor-name references
  gone (guard test); predecessor release-history docs dropped. **Gates:** functional suite green;
  coverage **99%** (≥95%); `ruff` zero; `mypy --strict` clean. Design/reference docs updated. Code review
  **waived** (bulk port; reviews resume M1). Issues #2–#13 closed.
- **M1 — Foundation & identity — ✅ 2026-10-10.** Quality-gate `Makefile`; full CLI command surface +
  reserved exit codes (`0–5`); fail-closed configuration (`ConfigError` → exit 2); real CI quality gate
  (ruff + mypy + pytest + coverage ≥95%); `doctor` + structured logging. **Gates:** functional suite green
  (1902+ passed, 0 skipped); coverage **99%** (≥95%); `ruff` zero; `mypy --strict` clean. Docs updated
  (README/CODEOWNERS/traceability/cli-reference). Issues #14–#24.
- **M2 — Pack format, loader & validation — ✅ 2026-10-12.** Versioned attack-pack schema (`pack` +
  `cases[]`); strict loader with file/line diagnostics and the **path-safety invariant** (predecessor G3
  closed); target/driver/oracle resolution via `attack_registry` (unknown → `ConfigError`, exit 2);
  `validate` recognizes attack packs (exit 2); `list packs`/`list cases` with tag/target/difficulty filters;
  v0.1.0 **catalog** (4 packs / 21 cases) + deterministic fixtures + benign-twin linkage + twin-driver hook;
  SHA-256 pack hashing + `min_agentdrill` gate. **Gates:** functional suite green; coverage **98.54%** (≥95%);
  `ruff` zero; `mypy --strict` clean. Docs updated (pack-format spec/design, pack-catalog, schema). Review
  findings #11–#15. Commits `935e5ec` (2.1 schema), `4e11c7b` (M2). Issues #106–#117.
- **M3 — Runner & execution spine — ✅ 2026-10-12.** `Run` + `CaseArtifact` models (reusing
  `TrajectoryStep`/`Cost`/`RunOutput`/`RunTimestamps`); `AttackRunner.run_one`/`run_all` with tag filtering
  and `.agentdrill/runs/<id>/` artifacts (`run.json` + `artifacts/<case_id>.json`); per-case **hard timeout in
  a separate process** (`status="timeout"`); **error capture / non-abort** (`status="error"` + traceback);
  `workers` + `max_outstanding` backpressure (parallel == serial, order preserved); **budget governor**
  (per-case `budget` + run-level `max_cost_usd` → `aborted: cost_exceeded`). **Gates:** suite green (1975
  passed); coverage **98.48%** (≥95%); `ruff` zero; `mypy --strict` clean. Docs updated (runner design,
  run-artifact spec). Review findings #16–#19. Issues #284, #118–#127.
- **M4 — Driver adapters — ✅ 2026-10-12.** Driver base + invocation contract (`build_payload` / `_invoke` /
  `run`, envelope normalization); **no ground-truth leakage** (oracles/expect never reach the driver);
  `subprocess` (stdin JSON → stdout envelope, raw-text fallback, `strict_output`), `python` (import +
  callable, hard timeout in a separate process), `http` (POST; timeout/connection/non-200 normalized),
  and per-harness `claude-code` / `cursor`; **registry + entry-point discovery**, unknown → `ConfigError`,
  and an `AdapterManifest` digest bound into `run.json`. **Gates:** suite green (2010 passed); coverage
  **98.30%** (≥95%); `ruff` zero; `mypy --strict` clean. Docs updated (adapter API, custom-adapter guide,
  run-envelope schema). Review findings #20–#23. Issues #128–#138.
- **M5 — Target adapters & recon/scoping — ✅ 2026-10-12.** `Target` ABC (`drive` / `read_decision` /
  `read_evidence`) + `CommandTarget`; the six deployed-stack targets (`agentgate`, `agentkeys`,
  `agentseatbelt`, `agentkernel`, `policyweave-output`, `agenthalt`) with a registry (unknown →
  `ConfigError`); **recon** (`ReconSnapshot`, `bind_cases` — a case on a nonexistent surface fails loudly;
  `mcp__server__tool` binds to its server); **attestation** hooks (`live`/`fixture`/`mock` + weakest-link);
  **model-surface sanity** (`check_model_surface` → 404/unreachable = clear `ConfigError`, closes G12); run
  layout stores target metadata + `recon.json` (`recon_ref`) so a run reconstructs its target. **Gates:**
  suite green (2046 passed); coverage **98.20%** (≥95%); `ruff` zero; `mypy --strict` clean. Docs updated
  (adapter API, recon design, attestation notes). Review findings #24–#27. Issues #139–#149.
- **M6 — Oracle engine — ✅ 2026-10-12.** `Oracle` ABC + registry (`@register_oracle` + entry-point discovery;
  unknown → `ConfigError`); **deterministic oracles** (`deny`/`allowed`/`confinement`/`budget`/`sequence`/
  `grounding`, reproducible); **judge oracles** (`judge`/`refusal-quality`/`explanation-adequacy`, mock +
  offline-gated providers, `temperature=0`, `{score, rationale}`); **hybrid engine** (deterministic gate
  always runs; judge only when the gate cannot confirm; offline → `judge_not_evaluated`); **dimensions +
  outcome split** (enforcement > integrity > compatibility); **divergence** (critical/warning) + **failure
  taxonomy**; **defense contracts** for the Wave-0 enforcers (CUJ-15). **Gates:** suite green (2086 passed);
  coverage **98.22%** (≥95%); `ruff` zero; `mypy --strict` clean. Docs updated (oracle design,
  failure-taxonomy reference). Review findings #28–#31. Issues #285, #150–#160.
- **M7 — Evidence integration — ✅ 2026-10-12.** agentwatch **schema reader** (`AgentWatchEvent`, typed;
  unknown event → `ConfigError`); **evidence binding** (`bind_case` → refs; empty → explicit `evidence_gap`);
  **expected-telemetry validation** (F52: `blocked` without its declared events → `telemetry_gap`);
  **evidence in artifacts** (`CaseArtifact.evidence` written to `artifacts/<case_id>.json`); **coverage
  reconciliation** (F26: exercised vs. unexercised surfaces; `gap:unexplained`). `Evidence` moved to
  `models/evidence.py` (SSOT). **Gates:** suite green (2109 passed); coverage **98.20%** (≥95%); `ruff` zero;
  `mypy --strict` clean. Docs updated (evidence-integration design, evidence-and-telemetry reference). Review
  findings #32–#35. Issues #161–#170.
- **M8 — Determinism — fixtures, manifest & pins — ✅ 2026-10-23.** `DriverFixture` (record/replay of
  driver target/tool responses; `record`/`replay`/`live`; loud on missing fixture / unsafe case id);
  `run-manifest.json` from the attack runner (`RunManifest` + `build_run_manifest`: host, pack hash,
  target/driver digests, oracles, pins, deps, env **names only**; `emit_manifest=False`); `PinSet` +
  `compare_pins`/`repin_note` (a changed pin is declared); `TrainingPosture`/`ContaminationProbe` with
  `CaseArtifact.contaminated` (F30, flagged never hidden); `verify_reproduction`/`fingerprint_artifacts`
  (rerun identical unless a pin changed, declared); public
  [determinism-methodology](../../reference/determinism-methodology.md). **Gates:** functional suite green
  (2140 passed, 0 skipped); coverage **98.18%** (≥95%); `ruff` zero; `mypy --strict` clean (175 files).
  Docs updated (storage-design, run-artifact-spec, reference index); traceability R6 updated. Review
  findings #36–#41. Commits `e74937f` (8.1), `de7ea0f` (8.2), `9fa601d` (8.3), `acd783d` (8.4),
  `fe7b337` (8.5), `c8bf77a` (8.6), + 8.D/8.CR. Issues #171–#181.
- **M9 — Golden results, comparison & attribution — ✅ 2026-10-23.** `Golden`/`GoldenCase` + `check_golden`
  (preregistered, locked per pack version; a differing candidate is flagged + re-pin note, DD-28);
  `GoldenStore` (`.agentdrill/goldens/<pack@version+hash>.json`, loud on missing/tampered/unsafe);
  `AttackComparisonEngine` (per-case / per-tag / aggregate deltas, `OutcomeSplit`); `detect_changes`
  (adapter/model/oracle swaps ≠ regression; `--allow-adapter-change`); `attribute_flip` (`attributed_to`
  + stage/mechanism + confidence, honest `unknown`) + `bisect_flip`; `classify_outcome` (adapter_failed /
  agent_crashed / scenario_failed + blocked/missed/degraded). **Gates:** functional suite green (2179
  passed, 0 skipped); coverage **98.18%** (≥95%); `ruff` zero; `mypy --strict` clean (181 files). Docs
  updated (comparison design normative + golden model; design/reference indexes); traceability R24 + F31.
  Review findings #42–#48. Commits `ef6b422` (9.1), `25d4b43` (9.2), `bf98048` (9.3), `af9d718` (9.4),
  `41edee7` (9.5), `cf67135` (9.6), + 9.D/9.CR. Issues #182–#192.
- **M10 — Honest reporter & public benchmark — ✅ 2026-10-23.** The `agentdrill/reporting/` package:
  multi-format reporter (JSON / Markdown / GitHub-Actions / self-contained HTML / PDF); `check_honesty` +
  `publish` (misses mandatory, R5); `seed_stats` + `require_multi_seed` (≥3-seed mean ± std, F29);
  `bootstrap_ci` / `RateCI` / `require_ci` (seeded CIs, bare % rejected, F55); `rate_finding` +
  `sort_findings` (attack-class × exposure severity, F41); `build_heatmap` + `HeatMap.delta` (F53);
  `TraceStore` (cell → trajectory + evidence, F56); `TrendStore` + `what_got_worse` (F23);
  `build_release` / `export_benchmark` / `reproduces` (publisher + submission, F57/R4). **Gates:**
  functional suite green (2232 passed, 0 skipped); coverage **98.12%** (≥95%); `ruff` zero; `mypy --strict`
  clean (192 files). Docs updated (reporting design normative; new reference
  reporting-and-statistics; reference index); traceability R4/R5/R19/R25/R29–R32. Review findings
  #49–#57. Commits `9decf8d` (10.1), `524a6d2` (10.2), `632b5ee` (10.3), `85be246` (10.4), `fa69095`
  (10.5), `d3ad3bb` (10.6), `941b83b` (10.7), `bcec473` (10.8), `cf339a4` (10.9), + 10.D/10.CR.
  Issues #193–#206.
- **M11 — CI gate, trigger/CART & local loop — ✅ 2026-10-23.** `agentdrill/ci/`: `run_exit_code` (0/1/2/
  3/4/5, most-severe-first; a must-block miss is 4, R3); `check_gates` (per-dimension + divergence
  gating, `--fail-on` / `--fail-on-divergence`); `render_ci_output` + `write_step_summary` (GitHub
  Actions/GitLab + `$GITHUB_STEP_SUMMARY`); `TriggerWatcher`/`ChangeEvent` (CART, F22); `LocalWatcher` +
  `snapshot_paths` and the wired `agentdrill watch` (dev loop, F68); `case_surfaces`/`affected_cases`/
  `selection` (diff-aware, F76); `annotate`/`github_annotation`/`build_alert`/`notify` (PR + webhook,
  F47); `DrillSchedule`/`due_drills`/`record_finding` and the wired `agentdrill schedule` (F71). **Gates:**
  functional suite green (2282 passed, 0 skipped); coverage **97.99%** (≥95%); `ruff` zero; `mypy --strict`
  clean (201 files). Docs updated (ci-gate design normative; new reference ci-integration; reference
  index); traceability R3. Review findings #58–#66. Commits `1277199` (11.1), `3136ac9` (11.2), `0914586`
  (11.3), `cfa3302` (11.4), `93cef32` (11.5), `57e65c6` (11.6), `519b629` (11.7), `e9989ba` (11.8), +
  11.D/11.CR. Issues #207–#218, #286.
- **M12 — Kill-time & kill-chain verification — ✅ 2026-10-23.** `agentdrill/killchain/`: the stage model
  + `KillChainTimeline`/`build_timeline` (missing stage `null` + flagged, 12.1); `run_cessation_probe`
  (revoke → re-attempt; `ceased` measured, not believed, 12.2); `compute_timing` (≥5-trial p50/p95/max per
  segment + total, 12.3); `analyze_timeline` (`kill_slow` / `detect_gap` / `decision_gap` / `halt_gap` /
  **`cease_gap`**, 12.4); `publish_budget`/`read_budgets` (versioned budgets in policyweave output, F78,
  12.5); `probe_evidence` (auditable re-attempt, 12.6). **Gates:** functional suite green (2316 passed,
  0 skipped); coverage **98.01%** (≥95%); `ruff` zero; `mypy --strict` clean (208 files). Docs updated
  (kill-chain design normative; new reference kill-chain-verification; reference index); traceability
  R8/R23. Review findings #67–#73. Commits `e5311e6` (12.1), `bccdb2f` (12.2), `97d550b` (12.3),
  `cb75301` (12.4), `5076fab` (12.5), `9e450b2` (12.6), + 12.D/12.CR. Issues #219–#229.
- **M13 — Efficacy control & utility-under-attack — ✅ 2026-10-23.** `agentdrill/efficacy/`: `run_efficacy`
  (unguarded twin; `efficacy_verified` iff the attack succeeds unguarded; `require_efficacy_backed`, F59,
  13.1); `INERT_FLAG`/`countable`/`enforcement_rate` (inert excluded from rates, 13.2); `assess_utility`
  (benign utility + utility-under-attack + enforcement rate; `utility_cost`, F51, 13.3); `run_cleanup`/
  `require_clean` (`dirty_target` release-blocking, F50, 13.4); `build_efficacy_report`/`efficacy_evidence`
  (per-case efficacy artifact, 13.5). **Gates:** functional suite green (2344 passed, 0 skipped); coverage
  **98.03%** (≥95%); `ruff` zero; `mypy --strict` clean (214 files). Docs updated (efficacy design
  normative; new reference efficacy-and-utility; reference index); traceability R26/R27/R33. Review
  findings #74–#79. Commits `7a42b0d` (13.1), `014d2d4` (13.2), `9ce4e4f` (13.3), `351d179` (13.4),
  `fbf78c4` (13.5), + 13.D/13.CR. Issues #230–#239.
- **M14 — Evasion pack & drill-the-drill — ✅ 2026-10-23.** `self-attack/` (evasion-self-attack.yaml +
  meta-verification.yaml + fixtures) and `agentdrill/security/`: `self_attack.assert_fail_closed`
  (every self-attack fails closed on enforcement/integrity, R7, 14.1); `meta_verification` (vacuous
  no-op not scored blocked; must-block miss exits non-zero; fixtures must intercept; attestation
  forgery; severity gaming — `require_meta_clean`, F43, 14.2); `holdout` (`PackGamingError` on
  published-green + holdout-red, F33, 14.3); `cadence` (evasion/meta/holdout every release,
  `CadenceError`, 14.4); `hidden_case` (independent-reviewer secret case escaping a single-layer
  defense, 14.5). **Gates:** functional suite green (2374 passed, 0 skipped); coverage **98.02%**
  (≥95%); `ruff` zero; `mypy --strict` clean (219 files). Docs updated (threat-model self-attack
  surfaces normative; new reference self-attack-and-meta-verification; reference index); traceability
  R7 + F33. Review findings #80–#86. Commits `12fbc83` (14.1), `8011f40` (14.2), `e741187` (14.3),
  `9ca4af4` (14.4), `d0ded9d` (14.5), + 14.D/14.CR. Issues #240–#249.
- **M15 — Attack chains & bounded adaptive orchestration — ✅ 2026-10-23.** `agentdrill/chains/`:
  `Chain`/`ChainStep`/`ChainOracle` + `run_chain` (state via `requires`; a stopped step halts the chain,
  15.1); `broke_at`/`furthest_reached` + `analyze_chain` (`on_time`/`late`/`never_broke`, 15.2);
  `AdaptiveCase` + `validate_adaptive`/`enforce_caps`/`is_golden_comparable` (provenance + documented
  mutations + caps, dual-use boundary, F40, 15.3); `AdaptiveRun`/`run_adaptive`/`record_adaptive`
  (pinned model + seed; mutation path in the manifest, 15.4); `require_reviewed`/`can_ship` (HITL gate,
  15.5). **Gates:** functional suite green (2401 passed, 0 skipped); coverage **98.05%** (≥95%); `ruff`
  zero; `mypy --strict` clean (226 files). Docs updated (new attack-chains design + reference;
  design/reference indexes); traceability R14/R16. Review findings #87–#93. Commits `e6341ea` (15.1),
  `8b5096c` (15.2), `8fea003` (15.3), `7facaa6` (15.4), `1f48fcc` (15.5), + 15.D/15.CR. Issues
  #250–#259.
- **M16 — Pack registry, signing & governance — ✅ 2026-10-23.** `agentdrill/registry/`: content-addressed
  signed index (`registry.json`, offline-verifiable, 16.1); `Signer`/`Verifier` + verified publishers
  (`sign_entry`/`verify_pack`/`require_verified`; unsigned/tampered/unknown rejected, 16.2); trust levels
  (`enforce_trust`; external ⇒ sandboxed subprocess only, never published, 16.3); contribution flow
  (`lint_pack` + `require_publishable`; unreviewed cannot publish, R11, 16.4); deprecation/takedown on a
  hash-chained `GovernanceLog` (16.5); `sync_index`/`is_outdated` + CLI `registry sync`/`pack outdated`
  (F75, 16.6). **Gates:** functional suite green (2438 passed, 0 skipped); coverage **97.94%** (≥95%);
  `ruff` zero; `mypy --strict` clean (234 files). Docs updated (new registry design + reference;
  design/reference indexes); traceability R11. Review findings #94–#100. Commits `232b629` (16.1),
  `e1ab08b` (16.2), `e6f6c09` (16.3), `af0ec7d` (16.4), `8325435` (16.5), `3b215a3` (16.6), + 16.D/16.CR.
  Issues #260–#270.
- **M17 — Interop, standards tagging & compliance — ✅ 2026-10-23.** `agentdrill/interop/`: importers for
  promptfoo/garak/AgentDojo/PyRIT (`import_suite`/`to_pack`, format translation only, F12, 17.1); ATLAS +
  OWASP tagging (`validate_tagging`, wired into lint, F13, 17.2); adversary profiles (`AdversaryProfile`,
  F54, 17.3); compliance mapping (EU AI Act Art.12 / NIST AI RMF / ISO 42001 + `export_agentcomply`,
  F24, 17.4); standards submission (NIST CAISI / AgentDojo-Inspect / OWASP Agentic) + OSS-Fuzz pack
  class (F28/R13, 17.5); competitor honest-coverage table (`reproduces`, R12, 17.6). **Gates:** functional
  suite green (2462 passed, 0 skipped); coverage **97.91%** (≥95%); `ruff` zero; `mypy --strict` clean
  (241 files). Docs updated (new interop design + reference; design/reference indexes); traceability
  R9/R10/R12. Review findings #101–#107. Commits `2ddf37b` (17.1), `5a85b2e` (17.2), `ce147db` (17.3),
  `ee607e2` (17.4), `b4e38bd` (17.5), `ca8b329` (17.6), + 17.D/17.CR. Issues #271–#281.
- **M18 — Lifecycle (intake, fix-validation, seams, attestation, verifier, quickstart) — ✅ 2026-10-23.**
  `agentdrill/lifecycle/`: intake SLA (`assess`, ≤7 days, F60, 18.1); fix-validation (`fix_decay`
  release-blocking, F61, 18.2); seam probing (`seam_gap` names both controls, F62, 18.3); attestation
  (weakest link; `mock` never publishes, F63, 18.4); standalone verifier (intact/complete/honest-shaped
  offline, F64, 18.5); evidence privacy (redaction receipts, F65, 18.6); quickstart (≤15 min, mock,
  watermarked, F66, 18.7); MCP + memory pack classes (F19/F20, 18.8); closes-the-loop policy suggestion
  (advisory, reviewed, F21, 18.9). **Gates:** functional suite green (2501 passed, 0 skipped); coverage
  **97.92%** (≥95%); `ruff` zero; `mypy --strict` clean (250 files). Docs updated (new lifecycle design +
  reference; design/reference indexes); traceability R34–R40. Review findings #108–#116. Commits
  `7712bd1` (18.1), `c36e530` (18.2), `7982c27` (18.3), `3056a37` (18.4), `b72f2a1` (18.5), `cabc948`
  (18.6), `b06b062` (18.7), `441c830` (18.8), `02fb0de` (18.9), + 18.D/18.CR. Issues #25–#38.
- **M19 — Oracle credibility — ✅ 2026-10-23.** `agentdrill/credibility/`: oracle versioning + release
  notes (`pin_versions`/`major_changed`/`rebaseline_note`, F79, 19.1); calibration corpus
  (`calibrate` → agreement/false-block/false-miss with CIs, F80, 19.2); judge drift (`detect_drift` →
  `judge_drift` release-blocking + prompt hash, F81, 19.3); meta-eval battery (`DEFAULT_BATTERY` +
  `run_battery`, F82, 19.4); human adjudication store + coverage stat (F83, 19.5); honesty labels
  (`experimental` cannot gate, F84, 19.6); dispute process (14-day SLA, CUJ-13, 19.7). **Gates:**
  functional suite green (2527 passed, 0 skipped); coverage **97.94%** (≥95%); `ruff` zero; `mypy
  --strict` clean (258 files). Docs updated (new oracle-credibility design + reference; design/reference
  indexes); traceability R21 + R53–R58. Review findings #117–#123. Commits `871bf5e` (19.1), `7f1c38c`
  (19.2), `374d273` (19.3), `054c175` (19.4), `397e4da` (19.5), `30ca529` (19.6), `5bc6a37` (19.7), +
  19.D/19.CR. Issues #39–#50.
- **M20 — Frontier & DX — ✅ 2026-10-23.** `agentdrill/dx/`: pack diff + coverage delta (`pack diff`, F67,
  20.1); dry-run/explain (zero executions, F69, 20.2); templates (mcp-poisoning/exfil-chain/
  destructive-command/supply-chain, F70, 20.3); CI-matrix export (`export ci`, F72, 20.4); programmatic
  assertions (F73, 20.5); provenance cards (F74, 20.6); read-only MCP drill surface (no write tools, F77,
  20.7); fleet mode (per-stack rollups, F45, 20.8). **Gates:** functional suite green (2560 passed,
  0 skipped); coverage **97.91%** (≥95%); `ruff` zero; `mypy --strict` clean (268 files). Docs updated
  (new frontier-dx design + reference; design/reference indexes); traceability R41–R52. Review findings
  #124–#131. Commits `8f2214a` (20.1), `bcb22a6` (20.2+20.3), `b933cdf` (20.4), `0f84bf3` (20.5),
  `b58969d` (20.6), `e5ebe7c` (20.7), `dd64343` (20.8), + 20.D/20.CR. Issues #51–#61, #282, #283.
- **M21 — Predecessor absorption & gap closure — ✅ 2026-10-23.** `agentdrill/parity/`: absorption ledger
  (delivered/delegated/waived, no silent drops, 21.1); G1–G14 gap closure (G7 SQLite waived by design,
  21.2); the parity gate (green for default, blocks on drift, 21.3); the predecessor retention plan
  (self-contained; M32 make-private, never delete, 21.4). **Gates:** functional suite green (2576 passed,
  0 skipped); coverage **97.93%** (≥95%); `ruff` zero; `mypy --strict` clean (273 files). Docs updated
  (new parity-and-gap-closure reference; reference index). Review findings #132–#135. Commits `6c9fd03`
  (21.1), `1c672e1` (21.2), `54c3611` (21.3), `3342e3f` (21.4), + 21.D/21.CR. Issues #62–#70.
- **M22 — NFRs, security hardening & resilience — ✅ 2026-10-23.** `agentdrill/hardening/`: performance
  budgets + parallel==serial + cache stats (22.1); fail-closed fault injection (runner/target/oracle/
  driver/tamper; a case failure never aborts the pack, 22.2); external-pack sandbox (`--network none`,
  read-only root, caps) + hash-chained tamper-evident audit (G4, 22.3); portability (3.10+, macOS/Linux,
  local-first, 22.4); cost controls (`--max-cost` aborts + reports, 22.5); self-observability run summary
  (dimensions + outcome split + exit code, 22.6). **Gates:** functional suite green (2595 passed,
  0 skipped); coverage **97.90%** (≥95%); `ruff` zero; `mypy --strict` clean (280 files). Docs updated
  (new hardening design + reference; design/reference indexes). Review findings #136–#142. Commits
  `78d5d05` (22.1), `ea97670` (22.2), `327e331` (22.3), `262d77c` (22.4), `d16f2ec` (22.5), `b001490`
  (22.6), + 22.D/22.CR. Issues #71–#81.
- **M23 — Independent effect witness & adversary lab — ✅ 2026-10-23.** `agentdrill/witness/` effect
  declarations + FS/network/credential/process/side-effect witnesses + the two-oracle verdict
  (`witness_discrepancy` first-class; `witness_unavailable`; live/none label; F87, 23.1–23.5);
  `agentdrill/lab/` seed-deterministic Adversary Lab + 12-carrier poisoned corpus + loopback-only
  isolation with `lab@version` pinned (F88, 23.6–23.8). **Gates:** functional suite green (2622 passed,
  0 skipped); coverage **97.92%** (≥95%); `ruff` zero; `mypy --strict` clean (290 files). Docs updated
  (effect-witness-and-lab design normative + new reference; design/reference indexes); traceability
  R61/R62. Review findings #143–#149. Commits `4c2d6bc` (23.1), `a924faf` (23.2), `dbd82bf` (23.3),
  `156e1f0` (23.4), `6470d5a` (23.5), `ff41cbb` (23.6), `2b3db1e` (23.7), `e926e7e` (23.8), +
  23.D/23.CR. Issues #288–#300.
- **M24 — Attacker strength, pressure & bypass search — ✅ 2026-10-23.** `agentdrill/attacker/`: attacker
  tiers (T0/T1/T2 + T3 deferred; tier+k+effort on every result, F85, 24.1); `Hold@k`/`ASR@k` metrics with
  bootstrap CIs + first-break p50/p95 + cost-to-break (F86, 24.2); pressure curves + auto claim scope +
  `brittle` label (24.3); the `Hold@k` gate (k=5/25; `Hold@5 < 100%` blocks, 24.4); the route-family
  library (8 families, ≥12 effects, F89, 24.5); a seeded, RoE-gated bounded search (24.6); delta-debug
  minimization + family dedup + auto-promotion to a regression (F61/F38, 24.7); the per-effect coverage
  report (24.8). **Gates:** functional suite green (2654 passed, 0 skipped); coverage **97.93%** (≥95%);
  `ruff` zero; `mypy --strict` clean (299 files). Docs updated (attacker-strength-and-bypass design
  normative + new reference; design/reference indexes); traceability R59/R60/R63. Review findings
  #150–#156. Commits `bff208f` (24.1), `96b7bf4` (24.2), `3465d97` (24.3), `339e6c8` (24.4), `a8ccd41`
  (24.5), `a4b8023` (24.6), `e398cfb` (24.7), `29a1d59` (24.8), + 24.D/24.CR. Issues #301–#313.
- **M25 — Bring-your-own-defense & neutral head-to-head — ✅ 2026-10-23.** `agentdrill/byod/`: the open
  Defense Contract + SDK (`config_digest`, decision points, I/O shape, evidence, fail-mode, version, ToS
  notes; F90, 25.1); the conformance kit (round-trip, determinism, evidence integrity, fail-mode; awards a
  level; 100% before listing, 25.2); the OSS-first Defense Zoo (3 adapters across 3 classes at v0.1.0,
  25.3); the neutral head-to-head (shared pack + seeds + twins across N defenses; `Hold@k`/`ASR@k`+CI,
  false-block, $/1k, latency, fail-mode; `composite_score` typed `None`, `rank_defenses` always raises;
  F91, 25.4); the neutrality process (pre-registration, published + equal rules, corrections log,
  author-overlap review; 25.5). **Gates:** functional suite green (2670 passed, 29 deselected, 0 failed);
  coverage **97.93%** (≥95%); `ruff` zero; `mypy --strict` clean (305 source files). Docs updated
  (byod-and-neutral-head-to-head design normative + reference; design/reference indexes); traceability
  R64/R65. Review findings #157–#165. Commits `89f3ee9` (25.1), `e9d3bf1` (25.2), `28e7960` (25.3),
  `d3737d6` (25.4), `7e8fffa` (25.5), + 25.D/25.CR. Issues #314–#323.
- **M26 — Security ecosystem integrations — ✅ 2026-10-24.** `agentdrill/integrations/`: the neutral
  `IntegrationFinding` projection; **SARIF 2.1.0** (rule=case, severity vector, tier, witness ref, ASI/ATLAS
  tags, stable `partialFingerprints`, suppressions=waivers) validated against the vendored **official OASIS
  schema** and **JUnit** (missed/degraded→failure, untested→skipped); **OTel** drill traces (`gen_ai.*`,
  pinned semconv, ≥95 % span-coverage gate); **OCSF** detection findings + **ECS** events, **OSCAL**
  assessment-results/POA&M, **STIX 2.1** bundles; **GitHub code-scanning** upload + **GitLab SAST** artifact +
  Slack/Teams/Jira/ServiceNow/PagerDuty/GitHub Issues/Linear adapters (stable keys, injected transport);
  **inbound import** (Inspect/promptfoo/garak/AgentDojo/PyRIT, `imported` trust, ≥95 % mapping gate) + inventory;
  **SIEM/EDR detection validation** (`alerted/detected/logged/missed` + p50/p95/max latency); **reliability**
  (retries+backoff, SQLite idempotent upserts, signed webhooks, durable offline spool, exactly-once replay).
  Closes **G14**. **Gates:** functional suite green (2743 passed, 29 deselected, 0 failed); coverage **98.01 %**
  (≥95 %); `ruff` zero; `mypy --strict` clean (320 files). Docs updated (new reference integrations; design
  integrations now built; reference/design indexes; traceability R74). Review findings #166–#173.
  Commits `e32af64` (26.1), `7d575ae` (26.2), `ff76541` (26.3), `61177bc` (26.4), `f18b67a` (26.5), `26e94a8`
  (26.6), `f983392` (26.7), + 26.D/26.CR. Issues #324–#335. **2 operational exit criteria (code-scanning
  upload ≥99 %, 24 h outage soak) deferred to M31 field verification.**

## Porting map (predecessor → agentdrill)

Source: the predecessor eval harness (`docs/PRD.md`, `docs/spec.md`, `docs/architecture.md`, scoring,
scenarios, CI, lessons) — **MIT; retired, retained privately, never deleted**. The port is a **bulk move
(M0)**; later milestones re-point the mechanics from *agent-quality grading* to *defense proof*.

| Shipped artifact | Ported at |
|---|---|
| Entire repo tree (`src/`, `tests/`, `scenarios/`, tooling, packaging, docs subset) | **M0** |
| Scenario-pack format; adapter contract; runner; trajectory capture | M0 → re-pointed M2–M4 |
| Deterministic + judge + hybrid scoring engine | M0 → re-pointed M6 |
| Fixture system / ToolStub; run manifest | M0 → re-pointed M8 |
| Baselines + comparison engine; report generation; CI exit codes | M0 → re-pointed M9–M11 |
| Sandbox / trust / audit / sanitization | M0 → re-pointed M16, M22 |
| Plugin registry (custom scorers/adapters) | M0 → re-pointed M4, M6 |
| Launch + security + adversarial packs | M0 → re-pointed M2, M14 |

> **Predecessor retention:** once M0 lands (code fully represented, ported suite green), agentdrill is
> self-contained; the predecessor is **made private and retained at M32 — never deleted**.

## PRD coverage matrix (every doc 00–43)

| PRD | Topic | Milestone(s) |
|---|---|---|
| **PRD 00** | Press Release / FAQ | narrative; validated at M32 |
| **PRD 01** | Why | context (all milestones) |
| **PRD 02** | Architecture | M0–M12 |
| **PRD 03** | Landscape / migration / predecessor (private) | M0, M21 |
| **PRD 04** | Users & CUJs (CUJ-1..63) | M2–M30 |
| **PRD 05** | What (Features) R1–R79 | M2–M30 |
| **PRD 06** | Security baseline / own threat model | M14, M22, M28 |
| **PRD 07** | Success metrics / release gate | M10, M31, M32 |
| **PRD 08** | Risks (RK-1..RK-16) | cross-cutting; M22 |
| **PRD 09** | Roadmap | M32 |
| **PRD 10** | Feature parity (absorption ledger) | M0–M20; gate M21, M32 |
| **PRD 11** | Decisions DD-01..DD-32 | cross-cutting (honored every milestone) |
| **PRD 12** | Traceability (maintained) | every milestone |
| **PRD 13** | Non-Functional Requirements | M22 |
| **PRD 14** | Non-goals (scope guard) | every milestone |
| **PRD 15** | Data model + lifecycle | M2, M9 |
| **PRD 16** | Attack-chain orchestration | M15 |
| **PRD 17** | Pack registry, signing & governance | M16 |
| **PRD 18** | Kill-chain verification & kill-time | M12 |
| **PRD 19** | Detection validation & BAS-class | M13 |
| **PRD 20** | Efficacy, freshness & lifecycle | M13, M18 |
| **PRD 21** | Pack catalog | M2, M14, M18, M27, M29 |
| **PRD 22** | Frontier & DX features | M11, M20 |
| **PRD 23** | Oracle credibility | M19 |
| **PRD 24** | Predecessor gap closure | M21 |
| **PRD 25** | Attacker strength & pressure curves | M24 |
| **PRD 26** | Independent effect witness | M23 |
| **PRD 27** | Adversary lab | M23 |
| **PRD 28** | Effect-based policy bypass search | M24 |
| **PRD 29** | Bring-your-own-defense & neutral head-to-head | M25 |
| **PRD 30** | Trace backtest & shadow mode | M27 |
| **PRD 31** | Attack-path graph & blast radius | M27 |
| **PRD 32** | Incident-to-pack compiler | M27 |
| **PRD 33** | Exposure ledger & time-boxed waivers | M28 |
| **PRD 34** | Drill attestations & deploy gate | M28 |
| **PRD 35** | Rules of engagement & safe-fire interlocks | M28 |
| **PRD 36** | Extension detonation lab | M29 |
| **PRD 37** | Break-It program | M29 |
| **PRD 38** | Security ecosystem integrations | M26 |
| **PRD 39** | Frontier attack classes | M29 |
| **PRD 40** | Trace explorer | M30 |
| **PRD 41** | Platform compatibility & support matrix | M30 |
| **PRD 42** | Standards, claims & interop | M26, M30 |
| **PRD 43** | Evidence register & method | cross-cutting (M0–M32) |

## Requirements detail (R1–R79)

| Req | Milestone(s) |
|---|---|
| R1 incident-replay packs | M2 |
| R2 run vs. deployed stack | M5 |
| R3 CI gate on policy PRs | M11 |
| R4 public reproducible benchmark | M10 |
| R5 honest reporting (misses) | M6, M10 |
| R6 determinism | M8 |
| R7 evasion pack | M14 |
| R8 kill-time | M12 |
| R9 interop import | M17 |
| R10 ATLAS/OWASP tagging | M17 |
| R11 community pack flow | M16 |
| R12–R13 competitor benchmark / fuzzing | M17, M20, M25 |
| R14–R18 chains / MCP packs / memory packs / mutation / closes-the-loop | M15, M18, M18, M15, M18 |
| R19–R21 statistical rigor / contamination / adjudication | M10 |
| R22–R25 defense contracts / kill-chain timing / attribution / severity | M7, M12, M9, M10 |
| R26–R32 BAS-class (cleanup, utility, telemetry, heat-map, profiles, CIs, traces, PR-submit) | M13 |
| R33–R40 efficacy / freshness / lifecycle | M13, M18 |
| R41–R52 frontier & DX | M20 |
| R53–R58 oracle credibility | M19 |
| R59–R60 attacker-strength tiers / pressure metrics | M24 |
| R61 independent effect witness | M23 |
| R62 adversary lab | M23 |
| R63 effect-based bypass search | M24 |
| R64–R65 defense contract/kit + neutral head-to-head | M25 |
| R66 trace backtest & shadow | M27 |
| R67 attack-path graph & blast radius | M27 |
| R68 incident-to-pack compiler | M27 |
| R69 exposure ledger & waivers | M28 |
| R70 drill attestations & deploy gate | M28 |
| R71 rules of engagement & safe-fire | M28 |
| R72 extension detonation lab | M29 |
| R73 Break-It program | M29 |
| R74 security ecosystem integrations | M26 |
| R75 frontier attack classes | M29 |
| R76 trace explorer | M30 |
| R77 platform compatibility matrix | M30 |
| R78 standards, claims & interop | M26, M30 |
| R79 evidence register & method | M0–M32 (cross-cutting) |

Full feature→requirement→test mapping: [PRD 05](../../prd/05-features.md) · [PRD 12](../../prd/12-traceability.md).

## CUJs (PRD 04)

CUJ-1 run pack → M5 · CUJ-2 gate PR → M11 · CUJ-3 reproduce benchmark → M10 · CUJ-4 drill incident → M2 ·
CUJ-5 kill-time → M12 · CUJ-6 evasion pack → M14 · CUJ-7 contribute/import → M17 · CUJ-8 close the loop →
M18 · CUJ-9 trend → M10 · CUJ-10 coverage → M10 · CUJ-11 offline bundle → M18 · CUJ-12 trigger re-drill →
M11 · CUJ-13 dispute → M19 · CUJ-14 attribute → M9 · CUJ-15 defense contract → M7 · CUJ-16 kill-chain →
M12 · CUJ-17 HITL → M19 · CUJ-18 fleet → M20 · CUJ-19 efficacy → M13 · CUJ-20 intake → M27 · CUJ-21 fix
holds → M18 · CUJ-22 seams → M18 · CUJ-23 verify standalone → M18 · CUJ-24 quickstart → M18 ·
CUJ-25 check the instrument → M19 · CUJ-26 run my oracle against the corpus → M19 · CUJ-27 schedule a
drill for a live adversary → M18.

**Addition CUJs (PRD 25–42):** CUJ-28 gate on "held every trial" → M24 · CUJ-29 read an honest number → M24 ·
CUJ-30 the log lied → M23 · CUJ-31 proof without telemetry → M23 · CUJ-32 author a rug-pull case → M23 ·
CUJ-33 carrier matrix → M23 · CUJ-34 bypass + minimal repro → M24 · CUJ-35 coverage not just green → M24 ·
CUJ-36 pick between defenses → M25 · CUJ-37 reproduce the OSS table → M25 · CUJ-38 don't ship the outage →
M27 · CUJ-39 shadow then promote → M27 · CUJ-40 trifecta inventory → M27 · CUJ-41 new path fails the gate →
M27 · CUJ-42 hours not days → M27 · CUJ-43 cite or drop → M27 · CUJ-44 sanctioned exception, visible miss →
M28 · CUJ-45 it expired → M28 · CUJ-46 admission gate on freshness → M28 · CUJ-47 underwriter verification →
M28 · CUJ-48 authorized to fire → M28 · CUJ-49 abort in seconds → M28 · CUJ-50 before allowlisting → M29 ·
CUJ-51 registry admission → M29 · CUJ-52 submit and get credit → M29 · CUJ-53 convert to a regression →
M29 · CUJ-54 inline in the PR → M26 · CUJ-55 did the SOC see it → M26 · CUJ-56 approval dialog truth → M29 ·
CUJ-57 contain the cascade → M29 · CUJ-58 red CI to root cause → M30 · CUJ-59 adjudicate at speed → M30 ·
CUJ-60 per-harness depth → M30 · CUJ-61 add my harness → M30 · CUJ-62 auditor evidence index → M30 ·
CUJ-63 contributor tag lint → M30.

## Decisions (PRD 11)

DD-01..DD-32 are honored across milestones (e.g., DD-01 no-enforcement → all; DD-05 agentwatch schema →
M7; DD-18 pins/manifest → M8; DD-20 untrusted packs → M16; DD-27 multi-seed → M10; DD-29 dark holdout →
M14). **Open additions** (from [PRD 43](../../prd/43-evidence-register-and-method.md) §PRD tensions): T1 the
deferred T3 adaptive tier, T2 no-composite-score vs. CVSS/AIVSS, T3 BYOD scope, T7 competitor-benchmark
legal shape — to be recorded as DD entries before the relevant milestones (M23–M30) close.

## v0.1.0 release gate (all milestones)

- [ ] M0–M32 exit criteria satisfied (incl. absorption + gap closure + design docs)
- [ ] Full PRD coverage delivered + tested; every R1–R79 demonstrated by an acceptance test
- [ ] The CI gate rejects an un-blocking policy change; the published benchmark reproduces; misses included
- [ ] Every published number carries attacker tier + k + CI and witness coverage ([PRD 25](../../prd/25-attacker-strength-and-pressure.md)/[26](../../prd/26-independent-effect-witness.md))
- [ ] NFRs met; fail-closed on tamper; untrusted packs sandboxed; zero out-of-scope actions ([PRD 35](../../prd/35-rules-of-engagement-and-safe-fire.md))
- [ ] Field tests pass (M31); security audit + compliance matrix + evidence indexes + release notes published (M32)
- [ ] SBOM + signed artifacts + drill attestation; OpenSSF Scorecard grade recorded
- [ ] **Predecessor repository retained and made private (not deleted)**

Review log: [codereview-log.md](codereview-log.md).
