# v0.1.0 Code Review Log

Record of substantive code-review findings per milestone. One row per finding; closed when fixed + tested.

| # | Milestone | Finding | Severity | Resolution | Status |
|---|---|---|---|---|---|
| 1 | M0 | `importlib.util.find_spec("google.adk")` raises `ModuleNotFoundError` on Python ≥3.13 when the `google` namespace is absent → collection error | Medium | guarded in `tests/test_adapters_adk_llm.py` + `tests/test_adapters_integration.py` | Resolved |
| 2 | M0 | `tests/test_docker.py::_docker_available()` checked only the docker CLI, so a stopped daemon triggered an image-build failure instead of a skip | Medium | probe `docker info` for the daemon | Resolved |
| 3 | M0 | omlx/Qwen judge wrapper: `output` returned as a JSON-encoded **string** was not unwrapped → silent `score 0.0` | High | `_parse_verdict` now parses a string `output` | Resolved |
| 4 | M0 | `tests/test_judge_omlx_integration.py` had no availability guard → hard failure when no omlx server | Low | module-level `skipif` on reachability | Resolved |
| 5 | M0 | pre-existing `scripts/wbs_issues.py` failed ruff repo-wide once a ruff config existed | Low | scoped, documented per-file-ignore | Resolved |
| 6 | M0 | coverage was **82%** (functional suite) against the milestone ≥95% gate | High | functional coverage raised to **99%** via added `tests/test_m0cov_*.py` | Resolved |
| 7 | M1 | global `--config` loads on every invocation; a config error exits 2 before the subcommand runs | Medium | fail-closed is intentional; doctor/--help unaffected; documented | Resolved |
| 8 | M1 | README referenced `make` targets (`drill-self`/`benchmark`/`verify-release`) that do not exist yet | Low | README rewritten to the real targets; `tests/test_identity_docs.py` guards README↔Makefile | Resolved |
| 9 | M1 | `types-pyyaml` lived only in `[dependency-groups].dev`, so `pip install .[dev]` / CI would fail `mypy --strict` on a fresh env | Medium | moved into `[project.optional-dependencies].dev` | Resolved |
| 10 | M1 | planned commands for later milestones are registered as stubs | Low | intentional (surface wired in 1.2); stubs fail loudly with reserved exit 2 | Resolved |
| 11 | M2 | Oracle vocabulary lived in two places (model `Literal`s **and** the registry) → drift risk; the design says oracle/target/driver unknowns are `ConfigError`, the spec called them schema validation | Medium | `attack_registry` is the single source of truth; schema holds open strings; unknown expect/dimension/telemetry/target/driver all raise `ConfigError` (exit 2) | Resolved |
| 12 | M2 | `agentdrill validate` exited **1** for a broken pack, but `errors.md` says invalid pack → exit **2**; the ported scenario-path test asserts 1 | Medium | attack packs now exit 2; the legacy scenario path stays at 1 (re-pointed later) so predecessor behavior is unchanged | Resolved (scoped) |
| 13 | M2 | spec rule 6 (`benign_twin` **required** for enforcement cases) not enforced | Low | only *dangling* `benign_twin` references are rejected now; requirement-presence is owned by the efficacy control (M13), where twin semantics are defined — enforcing it now would invent semantics | Open (deferred M13) |
| 14 | M2 | `list packs` / `list cases` were M1 planned-stubs asserted by `test_cli_surface` | Low | implemented; the planned-invocation list drops the two now-real commands | Resolved |
| 15 | M2 | isolated-adapter subprocess tests failed purely because the local `.venv` editable `.pth` still pointed at the pre-rename `agentsec-ecosystem/…` path, so child processes could not import `agentdrill` | Low (env) | local `.venv` `.pth` re-pointed to the renamed path; not a code defect (child processes rely on the installed package) | Resolved (env) |
| 16 | M3 | canonical per-case artifact named `CaseArtifact` while `design/runner.md` calls it `RunArtifact` | Low | `CaseArtifact` avoids clashing with the ported scenario `RunArtifact`; the mapping is documented in the design and the run-artifact spec | Resolved |
| 17 | M3 | per-case isolation (separate process) only engages when `timeout_seconds` is set; a literal "always separate process" reading would spawn a process per case on every run | Medium | `timeout_seconds` gates isolation (hard timeout when set, in-process otherwise); documented in `attack_runner` | Resolved (design intent) |
| 18 | M3 | the run-level `max_cost_usd` governor is inherently sequential, so it does not compose with `workers` parallelism | Low | when a run-level cap is set the governor runs cases in order; documented in `_run_budgeted` | Open (documented) |
| 19 | M3 | `attack_runner.py` coverage is 95% — the child-process entry (62–66) and dead-child branch (173–174) are not exercised in-process | Low | module still meets the ≥95% gate; the paths are exercised in real isolated runs | Accepted |
| 20 | M4 | design (`adapter-contract.md`) calls the driver return a `RunArtifact`; it is implemented as `CaseOutcome` to match the M3 spine contract | Low | the mapping is documented in the design + adapter-api; the runner wraps `CaseOutcome` into `CaseArtifact` | Resolved |
| 21 | M4 | the design's payload field list (`input`/`allowed_tools`/…) is the predecessor **scenario** shape; an attack case has no such fields | Medium | `build_payload` emits `case_id`/`goal`/`target`/`attack`/`budget`; the leakage guard asserts no `oracle`/`expect`/telemetry/benign-twin ever appears | Resolved |
| 22 | M4 | drivers raise `ConfigError` for missing required config (`command`/`url`/`module`) and `AdapterError` for runtime failures | Low | matches the error contract (invalid config → exit 2; runtime failure → `status`) | Resolved |
| 23 | M4 | entry-point `discover()` finds no community drivers in CI | Low | no-op by design; `discover` accepts an explicit iterable so registration is tested deterministically | Resolved |
| 24 | M5 | the deployed-stack targets drive components through a configured command (no real components in CI) | Medium | `CommandTarget` + per-component subclasses exercise the component's command/interface; the real path is the configured component | Resolved (design-consistent) |
| 25 | M5 | recon treats an `mcp__<server>__<tool>` tool as present when its server is in `mcp_servers` | Low | documented in `ReconSnapshot.has_tool` | Resolved |
| 26 | M5 | `weakest_link([])` returns `mock` (conservative) rather than `live` | Low | documented; an empty chain never over-claims `live` | Resolved |
| 27 | M5 | model-surface check GETs `{base_url}/models` and maps 404 / connection errors to `ConfigError` | Low | closes predecessor gap G12; clear failure before any case runs | Resolved |
| 28 | M6 | the deterministic oracles implement concrete rules for deny/allowed/confinement/budget/sequence/grounding that the design names but does not specify | Medium | each rule is documented per-oracle (rationale) and in `reference/failure-taxonomy.md`; all are pure functions of case/observation | Resolved |
| 29 | M6 | "judge runs only where needed" is implemented as: the judge runs only when the deterministic gate cannot confirm the case's expected outcome | Low | documented in `OracleEngine.evaluate` | Resolved |
| 30 | M6 | real judge providers (openai/anthropic/ollama/mlx) fail loudly offline (`ConfigError`) instead of silently skipping the judge | Low | only `mock` resolves offline; providers land with their SDKs | Resolved |
| 31 | M6 | divergence classification: gate `missed`/`degraded` + judge `blocked` → critical, otherwise warning | Low | documented in `classify_divergence`; gated by `has_divergence` (`--fail-on-divergence`) | Resolved |
| 32 | M7 | `Evidence` was defined in `targets/base.py`, which would cycle once run artifacts needed it | Medium | moved to `models/evidence.py` (SSOT); `targets.base` re-exports it; oracles/artifacts import from `models` | Resolved |
| 33 | M7 | `telemetry_gap` was missing from the failure-taxonomy literal | Low | added to `FailureType`; used by the telemetry validator | Resolved |
| 34 | M7 | evidence binding keys on `AgentWatchEvent.case_id` | Low | events without a `case_id` do not bind (documented); an empty binding → `evidence_gap` | Resolved |
| 35 | M7 | coverage `unexplained` = unexercised surfaces without an explanation (sorted) | Low | documented; `gap_unexplained` property | Resolved |
| 36 | M8 | storage-design's manifest lists `oracles: [{name, version}]`, but oracles carry **no** version | Low | `oracles` field emitted (empty until an oracle engine is bound); no version invented — populated when oracle versioning lands | Open (documented) |
| 37 | M8 | `--fixtures` / `--live` mutual exclusivity lives on the grading `run` CLI; the attack path has no CLI yet | Low | `DriverFixture` validates the mode and requires a source for `record`/`live`; CLI parity retained (`test_m0cov_cli`) | Resolved |
| 38 | M8 | a recorded fixture keyed by case id could traverse the fixtures directory | Low | `DriverFixture._fixture_path` rejects a separator/`..`/empty case id loudly (closes predecessor path-safety G3 for fixtures) | Resolved |
| 39 | M8 | `RunManifest.dependencies` renamed to `deps` to match the storage design — a model shared with the grading path | Medium | grading manifest tests re-run; both manifest shapes round-trip | Resolved |
| 40 | M8 | the contamination probe matches a **declared** training posture (case id / incident ref / tool), not model internals | Low | documented in `determinism-methodology.md`; no invented introspection — the exposure surface is an input | Resolved (scoped) |
| 41 | M8 | a declared re-pin makes `ReproductionResult.ok` true even when results differ | Low | intentional (DD-28): a changed pin is the sanctioned, declared exception; a silent difference still fails | Resolved (design intent) |
| 42 | M9 | a new attack-path comparison would duplicate the ported scenario `ComparisonEngine` | Medium | the two consume different data models (scenario `RunScore` vs attack `CaseArtifact` outcomes); the attack engine lives in `comparison/attack_engine.py` and reuses `OutcomeSplit`; the ported engine is untouched | Resolved (two models) |
| 43 | M9 | golden direction ranks `blocked > degraded > missed`, but a *benign twin* inverts the sign (blocked = over-block = bad) | Low | the rank matches the design's "blocked→missed flip is a regression"; twin-aware sign is owned by the efficacy control (M13) | Open (deferred M13) |
| 44 | M9 | `Golden.created` uses `now()` so two equal goldens are not `==` | Low | equality is over content; tests compare `pack_ref`/`cases`/`pins`; `created` is metadata | Resolved (documented) |
| 45 | M9 | change detection compares driver/target **digests** and pins, not arbitrary target-config fields | Medium | a driver/target digest changes when its adapter changes; finer target-config diffs are passed to attribution via `config_diffs` | Resolved |
| 46 | M9 | attribution priority (oracle > adapter > model > target_config) is a fixed heuristic | Low | competing signals lower confidence (0.5 vs 0.9); an uncorrelated flip is `unknown` (never guessed); CI can `bisect_flip` across intermediate configs | Resolved (documented) |
| 47 | M9 | outcome classification keys on `CaseArtifact.status` + error substrings for error-type | Low | documented mapping; `adapter_failed` markers are explicit in `_ADAPTER_MARKERS` | Resolved (documented) |
| 48 | M9 | the golden store path uses `pack_ref` in the filename | Low | `_unsafe` rejects separators/`..`/`~`/empty; a tampered `pack_ref` fails loudly on load | Resolved |
| 49 | M10 | PDF is a minimal hand-built single-page document (no PDF dependency) | Low | valid `%PDF`/`%%EOF`; a long report overflows one page — acceptable for a compliance summary now | Open (documented) |
| 50 | M10 | HTML is deliberately non-interactive (inline CSS, no scripts, no network) | Low | self-contained/offline by requirement; a script-free rendering | Resolved (design intent) |
| 51 | M10 | an empty report (zero rows, zero split) passes the honesty check | Low | nothing is hidden when there is nothing; a run with cases always carries its rows | Resolved (documented) |
| 52 | M10 | bootstrap uses a seeded `random.Random` (`noqa: S311`) | Low | reproducible by design; not cryptographic (not needed) | Resolved (design intent) |
| 53 | M10 | the severity rubric (class weight + exposure weight → level) is a fixed documented heuristic | Low | the mapping is explicit and testable; tunable later without changing the interface | Resolved (documented) |
| 54 | M10 | the heat-map uses case tags as controls; `untested` = an absent cell | Low | a dedicated control registry can replace tags without changing `HeatMap` | Resolved (scoped) |
| 55 | M10 | `TraceStore` keys on `trace_ref` (falling back to case id); a duplicate key overwrites (last wins) | Low | documented; trace refs are expected unique per run | Resolved (documented) |
| 56 | M10 | `what_got_worse` compares only the two latest releases (one-call query); `deltas(klass)` gives the full series | Low | matches the F23 "what got worse" query; the series is available | Resolved (design intent) |
| 57 | M10 | `reproduces` compares rate points within tolerance + miss sets; CIs need not match | Low | a re-run's bootstrap CI may differ by resampling; the point estimate is the reproduced number | Resolved (documented) |
| 58 | M11 | `agentdrill.ci` imports `ExitCode` from `agentdrill.cli.exit_codes` | Low | `ExitCode` is the reserved-code SSOT; the CLI package import is light (no command side effects) | Resolved (SSOT) |
| 59 | M11 | the dimension gate keys on verdict `dimensions` and a 0.8 blocked-rate threshold | Low | the threshold is configurable; each dimension is independent | Resolved (documented) |
| 60 | M11 | `render_ci_output` supports `github-actions` and `gitlab` only | Low | an unknown format fails loudly; more are additive | Resolved (documented) |
| 61 | M11 | the CART watcher selects by exact surface string (no globs/labels yet) | Low | surfaces are the pack's bound targets/tools; glob/scope can layer on later | Resolved (scoped) |
| 62 | M11 | `agentdrill watch` surfaces the affected set but re-run wiring comes from config | Low | the selection engine is the deliverable; the CLI reports the affected packs; `--once` is CI-safe | Resolved (scoped) |
| 63 | M11 | `affected_cases` includes a case when **any** bound surface changed (superset by design) | Low | the changed-surface set equals the bound set (F76 acceptance) | Resolved (design intent) |
| 64 | M11 | `notify`'s default poster uses `urllib` (`noqa: S310`) with an operator-configured URL | Low | injectable poster for tests; no-op without a webhook | Resolved (design intent) |
| 65 | M11 | `agentdrill schedule` reads schedules from config; with none it reports zero due | Low | the schedule engine + finding files are the deliverable; `--once` is CI-safe | Resolved (scoped) |
| 66 | M11 | watch/schedule were removed from the CLI *planned* stubs; `test_cli_surface` updated | Low | a now-real command is no longer a planned stub (as with `list packs` at M2) | Resolved |
| 67 | M12 | the timeline stores stage times as seconds since `attack_start`, not absolute timestamps | Low | durations/percentiles need relative times; `attack_start` anchors the run | Resolved (documented) |
| 68 | M12 | a missing stage is `null` + `missing`, never inferred/back-filled | Low | the design invariant (detection is not safety) | Resolved (design intent) |
| 69 | M12 | the cessation probe's `reattempt` returns a bool (still-acting); the cli/target wiring is caller-supplied | Low | keeps the probe pure and testable; the target drives the real re-attempt | Resolved (scoped) |
| 70 | M12 | a stage is "dominant" only when it is the largest and ≥ `min_gap_seconds` (0.5) | Low | avoids firing on a balancing tie of tiny segments; threshold configurable | Resolved (documented) |
| 71 | M12 | `cease_gap` fires when revoked but never ceased **or** `revoked→ceased` dominates | Low | the design's "nonzero/dominant" signature; highest severity | Resolved (design intent) |
| 72 | M12 | `total_duration` needs `attack_start` and a later stage; otherwise the total is unmeasurable (`n=0`) | Low | honest: no total rather than a guessed one | Resolved (documented) |
| 73 | M12 | kill-time budgets live as a versioned `kill_time` block inside policyweave output | Low | co-location means a budget change lands in the same PR as its rule (F78) | Resolved (design intent) |
| 74 | M13 | the unguarded twin's success is a caller-supplied `Callable[[], bool]` (the target drives the real attack) | Low | keeps the control pure/testable; the runner supplies the twin | Resolved (scoped) |
| 75 | M13 | `enforcement_rate` is `blocked/(blocked+missed)` over efficacy-verified cases; `None` when none are countable | Low | an all-inert set yields no number rather than a fake one | Resolved (documented) |
| 76 | M13 | `utility_cost` fires at enforcement ≥0.8 with collapsed utility-under-attack | Low | threshold `HIGH_ENFORCEMENT` is explicit/configurable | Resolved (documented) |
| 77 | M13 | cleanup runs after every case via `cleanup_after_case`; a raise is captured as dirty | Low | timeout/error cases still clean the target; a raise never hides the dirt | Resolved (design intent) |
| 78 | M13 | `dirty_target` is release-blocking via `require_clean` (`DirtyTargetError`) | Low | a dirty target invalidates later numbers (Caldera/ART discipline) | Resolved (design intent) |
| 79 | M13 | the efficacy artifact ships an `Evidence(event="efficacy")` per case | Low | reuses the `Evidence` SSOT; per-case visibility (CUJ-11) | Resolved |
| 80 | M14 | the self-attack suites live under `self-attack/`, not the public `packs/` catalog | Medium | a self-attack suite is CI-run, not a user catalog entry; keeps the public catalog stable (loaded explicitly) | Resolved (scoped) |
| 81 | M14 | `check_no_vacuous_block` defines "vacuous" as no trajectory **and** no output | Low | the minimum signature of a no-op; a real block carries a deny trace/output | Resolved (documented) |
| 82 | M14 | `check_must_block_exits_nonzero` is gamed when the gate exits 0 with an unconfirmed must-block case | Low | reuses `ci.run_exit_code`; a `forced_exit_code` lets meta cases assert a silent gate | Resolved (design intent) |
| 83 | M14 | `check_no_severity_gaming` compares the claimed severity to the F41 rubric | Low | reuses `reporting.rate_finding` (SSOT); a weaker claim is gaming | Resolved |
| 84 | M14 | the dark holdout registry keeps the private subset in memory | Low | the subset is unpublished; persistence lands with the registry (M16) | Resolved (scoped) |
| 85 | M14 | `escapes_single_layer` requires **all** of `HIDDEN_REQUIRED_LAYERS` present | Low | the hidden case defeats any single control by construction | Resolved (design intent) |
| 86 | M14 | the hidden case is reachable in the meta pack (not compiled-away) | Low | a reviewer-authored secret case is intentionally kept in the pack for the meta run | Resolved (design intent) |

> **M0 review scope:** M0 is a bulk **port** of existing predecessor code (already reviewed upstream). A separate
> formal code review is **waived for M0** per maintainer; the findings above are the port-induced items found and
> fixed during the port. Formal reviews resume at M1.

## Review checklist (per PR)

- [ ] Correctness: does it do what the linked WBS item says?
- [ ] Tests: do new paths have tests? coverage ≥95%?
- [ ] Security: no secrets/PII persisted; untrusted packs sandboxed; fail-closed on tamper
- [ ] Determinism: results reproduce (pins + manifest); no silent pin change
- [ ] Honesty: misses present; no green without efficacy; `mock` never publishes
- [ ] Lint/types: ruff zero; mypy strict clean
- [ ] Docs: requirement→test mapping updated ([PRD 12](../../prd/12-traceability.md)); traceability + WBS checkpoint
- [ ] Non-goals: no detection claims, no enforcement, no novel-capability drift ([PRD 14](../../prd/14-non-goals.md))

## Milestone closure checklist (per milestone)

- [ ] Every work item implemented (no partials); test-first where the item is a behavior
- [ ] Milestone gates run **once at end**: full suite · coverage ≥95% · `ruff` · `mypy --strict`
- [ ] Committed · pushed · tracking issue closed (or commented)
- [ ] Design/reference docs updated + linked from the WBS
- [ ] Checkpoint appended to the [WBS index](wbs-v0.1.0-index.md) Progress section (commit refs + gate result)
