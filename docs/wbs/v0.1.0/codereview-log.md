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
| 87 | M15 | a chain step's `requires` condition is parsed as `<step>.succeeded` | Low | the grammar is documented; a malformed condition names an unreached step | Resolved (documented) |
| 88 | M15 | a stopped step halts the whole chain (later steps are not reached) | Low | the design reading: once broken, the attack cannot progress | Resolved (design intent) |
| 89 | M15 | `on_time`/`late`/`never_broke` are three distinct findings, not a pass/fail | Low | a defense that breaks the chain too late is a chain-level miss | Resolved (design intent) |
| 90 | M15 | `validate_adaptive` permits only `MUTATION_KINDS` (paraphrase/encoding/argument/order) | Low | the dual-use boundary: mutation only, no novel capability (RK-2) | Resolved (design intent) |
| 91 | M15 | `run_adaptive` is a pure function of `(case, model, seed)` | Low | determinism requires no live target in the path computation; responses pin separately | Resolved (documented) |
| 92 | M15 | `AdaptiveRun.digest` binds model + seed + path | Low | a different seed/model yields a different recorded path (reproducibility) | Resolved (design intent) |
| 93 | M15 | adaptive cases are excluded from golden-locked comparisons | Low | they explore; they must not anchor a golden (RK-13) | Resolved (design intent) |
| 94 | M16 | the default signer is a stdlib HMAC (`HmacSigner`), not Sigstore | Medium | `cryptography` is not a declared dependency; the `Signer`/`Verifier` interface is the seam — the production path binds a Sigstore identity (16.2) without changing callers | Open (documented) |
| 95 | M16 | `content_address` is a SHA-256 over canonical pack JSON | Low | deterministic and publisher-independent; identical content ⇒ identical address | Resolved (design intent) |
| 96 | M16 | `verify_pack` also checks the publisher's bound key id against the verifier | Low | an unknown publisher or a key mismatch is rejected before install | Resolved (design intent) |
| 97 | M16 | trust enforcement reuses the ported `security.policy.TrustPolicy` and normalizes `built-in`↔`builtin` | Low | single source of truth for the trust matrix; the two labels are reconciled | Resolved (SSOT) |
| 98 | M16 | `lint_pack` requires a `methodology` argument (path) | Low | the contribution flow expects a published methodology; absence is a lint finding | Resolved (documented) |
| 99 | M16 | `pack verify` / `pack publish` remain planned CLI stubs (engines shipped) | Low | the engines (`verify_pack`/`require_publishable`) are done and tested; the CLI wiring is additive | Open (deferred) |
| 100 | M16 | `registry sync` and `pack outdated` read a local signed file (no live network client) | Low | offline-verifiable by design; a network mirror is a thin fetch in front of the same verify | Resolved (scoped) |
| 101 | M17 | interop importers target a documented minimal export shape per tool (not every tool version) | Medium | format translation is version-tolerant by design; the normalized `ImportedCase` insulates the core | Resolved (scoped) |
| 102 | M17 | an imported pack defaults every case to `expect: blocked` on `policyweave-output`/`subprocess` | Low | a translated suite asserts the stack fails closed; the source's exact oracle is not always present | Resolved (documented) |
| 103 | M17 | standards tagging is enforced via `validate_tagging` + the lint `standards` check | Low | the M16 contribution lint now requires ATLAS + OWASP tags; its test fixture was updated | Resolved |
| 104 | M17 | the compliance mapping is a static finding-type → control table | Low | explicit and testable; new finding types are additive | Resolved (documented) |
| 105 | M17 | `export_agentcomply` writes a local JSON artifact (no network to agentcomply) | Low | offline by design; agentcomply consumes the file | Resolved (scoped) |
| 106 | M17 | `fuzz_class_pack` is a minimal single-case OSS-Fuzz-class pack | Low | the pack class is the invariant; a real corpus layers on | Resolved (scoped) |
| 107 | M17 | `competitor.reproduces` compares outcome splits + seeds, not CIs | Low | the honest-coverage number is the reproduced quantity (as in M10) | Resolved (documented) |
| 108 | M18 | the intake SLA is measured from a supplied `days_elapsed`, not wall-clock | Low | keeps triage deterministic/testable; a caller passes the real elapsed days | Resolved (scoped) |
| 109 | M18 | `fix_validation` models a regression case as `decayed` when the observed outcome ≠ `blocked` | Low | the fix's invariant is "the attack stays blocked"; any other outcome is decay | Resolved (design intent) |
| 110 | M18 | `probe_seam` models the two-control composition as first-denied / second-allowed | Low | captures the seam invariant; the real controls supply the booleans | Resolved (scoped) |
| 111 | M18 | `attestation` reuses the M5 `weakest_link` SSOT | Low | one realness vocabulary (live/fixture/mock) across the system | Resolved (SSOT) |
| 112 | M18 | the verifier's `honest_shaped` requires ≥3 seeds + a non-empty split + no composite score | Low | mirrors the M10 publish rules; offline and structural | Resolved (design intent) |
| 113 | M18 | `privacy` redacts a fixed set of classes (secret/token/email) | Low | additive: new classes are a pattern entry; receipts carry class/count/location | Resolved (scoped) |
| 114 | M18 | quickstart runs the bundled demo pack with a mock driver under a temp runs dir | Low | mock-attested and watermarked — the first result is demo, never evidence | Resolved (design intent) |
| 115 | M18 | the MCP/memory packs add cases to the public catalog (fixtures + catalog test updated) | Low | the classes are shipped packs (F19/F20); the catalog grows from four to six | Resolved |
| 116 | M18 | `policy_suggestion` emits an advisory rule + what-if; never auto-applies | Low | the fix is a reviewed PR (F21); `auto_applied` is always false | Resolved (design intent) |
| 117 | M19 | `parse_semver` is lenient (missing parts → 0) | Low | accepts `2` / `2.1`; a malformed string raises `ValueError` | Resolved (documented) |
| 118 | M19 | the calibration corpus is caller-supplied (no bundled public corpus file yet) | Low | the report/publish shape is the deliverable; a corpus file is additive | Resolved (scoped) |
| 119 | M19 | `detect_drift` treats only a change vs `previous_outcomes` as a flip | Low | drift needs a baseline; a first run has none and cannot drift | Resolved (design intent) |
| 120 | M19 | the meta-eval `DEFAULT_BATTERY` uses semantic kinds incl. `seam_gap`/`inert` | Low | covers the outcome + integrity kinds; `verdict_of` is injected | Resolved (documented) |
| 121 | M19 | `AdjudicationStore.record` replaces a prior verdict for the same case | Low | one current human label per case; history is a future concern | Resolved (documented) |
| 122 | M19 | honesty labels default to none; `can_gate_ci` treats anything but `experimental` as gate-capable | Low | the strict rule is "experimental cannot gate"; other labels are gate-capable | Resolved (design intent) |
| 123 | M19 | the dispute SLA is measured from a supplied `days_elapsed` | Low | deterministic/testable; the caller passes real elapsed days (as with intake) | Resolved (scoped) |
| 124 | M20 | `diff_packs` compares case content by a canonical SHA-256 of the case model | Low | deterministic; a whitespace-only change in canonical JSON is not a case change | Resolved (design intent) |
| 125 | M20 | dry-run emits a plan without a runner (guaranteed zero executions) | Low | the plan is derived from the pack; `executions` is always 0 | Resolved (design intent) |
| 126 | M20 | templates use a small fixed tool/target/tag set per kind | Low | scaffolds pass lint + carry a benign twin; richer stubs are additive | Resolved (scoped) |
| 127 | M20 | `export ci` seeds the manifest hashes/attestation with placeholders | Low | the matrix shape is the deliverable; a real run fills the manifest | Resolved (scoped) |
| 128 | M20 | assertions accept a `Verdict` or an outcome string | Low | works over the same run objects; strings ease host-test embedding | Resolved (documented) |
| 129 | M20 | `validate_card` requires reviewers + sources non-empty | Low | a provenance card without reviewers cannot render | Resolved (design intent) |
| 130 | M20 | `is_write_tool` matches by substring tokens | Low | a conservative read-only guard; `require_read_only` rejects any write tool | Resolved (design intent) |
| 131 | M20 | fleet outliers key on a per-stack blocked-coverage threshold | Low | per-stack honest coverage; the threshold is caller-supplied | Resolved (documented) |
| 132 | M21 | the absorption ledger ships a representative capability set (not the full PRD 10 enumeration) | Low | the ledger shape + gate are the deliverable; rows are additive | Resolved (scoped) |
| 133 | M21 | gap evidence cites test files (strings), not live test execution | Low | the gate asserts completeness; the cited tests run in the suite | Resolved (documented) |
| 134 | M21 | `parity_gate` is green for the default ledger/gaps and red on drift | Low | CI-enforced; `require_parity` raises `ParityError` | Resolved (design intent) |
| 135 | M21 | the retention plan records the M32 make-private instruction; it does not perform it | Low | M32 is the release-readiness milestone; this records the plan | Resolved (design intent) |
| 136 | M22 | `measure_budget` takes an observed elapsed time (no in-process timing) | Low | keeps the budget check pure/testable; the runner supplies elapsed | Resolved (scoped) |
| 137 | M22 | `run_fault` treats "raised" as fail-closed; a swallowed fault is flagged | Low | a fault must surface loudly — never silently green | Resolved (design intent) |
| 138 | M22 | `sandbox_spec_for` returns a strict spec for external and a permissive one otherwise | Low | the guard (`require_sandbox`) only constrains external | Resolved (design intent) |
| 139 | M22 | `AuditChain` is an in-memory hash chain (the on-disk audit trail is `security/audit.py`) | Low | the chain shape proves tamper-evidence; persisted entries bind the same digests | Resolved (scoped) |
| 140 | M22 | portability checks take `python_version`/`system` params (defaulting to the runtime) | Low | deterministic tests; defaults read the real environment | Resolved (documented) |
| 141 | M22 | cost controls report; the runner's `max_cost_usd` governor does the actual abort | Low | reuses M3's budget governor; the report is the shareable summary | Resolved (SSOT) |
| 142 | M22 | `RunSummary` folds verdict dimensions + outcome split + exit code | Low | one summary answers "what happened"; reuses `outcome_split` | Resolved (SSOT) |
| 143 | M23 | effect declarations are a separate schema (`witness/effects.py`), loader support is additive | Low | the declaration shape is the deliverable; pack YAML binding is additive | Resolved (scoped) |
| 144 | M23 | `file_fingerprint` returns `("absent", 0)` for a missing file | Low | a created canary is a change; absent is a distinct fingerprint | Resolved (documented) |
| 145 | M23 | `Sinkhole` is in-memory; `url()` composes a loopback URL with the token | Low | the recording surface is the deliverable; a live listener is deployment | Resolved (scoped) |
| 146 | M23 | `two_oracle_verdict` maps defense × witness to five outcomes + a finding | Low | disagreement (`witness_discrepancy`) is first-class; `witness_unavailable` is labeled | Resolved (design intent) |
| 147 | M23 | `AdversaryLab` records a deterministic event log from explicit calls | Low | same seed + same calls ⇒ same log (≥99.9%); the seed pins the schedule | Resolved (design intent) |
| 148 | M23 | carriers are template strings (≥12) rendered with an instruction | Low | the carrier matrix is runnable; real files render from the same templates | Resolved (scoped) |
| 149 | M23 | `LabIsolation` enforces a loopback allowlist; `pin_lab` records `lab@version` | Low | zero non-loopback egress; the version binds the lab into the manifest | Resolved (design intent) |
| 150 | M24 | `TierLabel` effort labels are fixed per tier; k is caller-supplied | Low | every published result carries tier + k + effort | Resolved (documented) |
| 151 | M24 | `Hold@k` windows are `all(trials[i:i+k])`; `ASR@k` is the complement | Low | all-of-k vs any-of-k; bootstrap CIs on both | Resolved (design intent) |
| 152 | M24 | a pressure curve is `brittle` when T0 holds but T2 breaks | Low | the label surfaces a mutation-only weakness | Resolved (design intent) |
| 153 | M24 | the `Hold@k` gate defaults to k=5 (PR) / k=25 (nightly) at 100% | Low | configurable; `Hold@5 < 100%` blocks critical must-block cases | Resolved (design intent) |
| 154 | M24 | the route catalog ships >= 12 effects over the 8 families | Low | `require_reviewed` mirrors pack review | Resolved (scoped) |
| 155 | M24 | `bounded_search` is seeded breadth-over-families then depth, RoE-gated | Low | same seed ⇒ same sequence; runs only under RoE | Resolved (design intent) |
| 156 | M24 | `promote_to_regression` reuses the M18 `regression_case` (F61) | Low | a confirmed bypass becomes a permanent pinned regression in the same release | Resolved (SSOT) |
| 157 | M25 | `config_digest` hashes canonical JSON (`sort_keys`, compact separators) | Low | key order never changes a digest; cells bind to the defense's config | Resolved (documented) |
| 158 | M25 | `DefenseSDK` wraps an arbitrary `decide` callable; no engine coupling | Low | the adapter contract is the deliverable; drivers stay in M4 | Resolved (scoped) |
| 159 | M25 | the conformance kit reuses one `sample_requests` set for round-trip and determinism | Low | determinism compares repeated calls; non-determinism fails | Resolved (design intent) |
| 160 | M25 | `ConformanceResult.passed` is `True` only for a non-empty all-ok check set | Low | an empty kit never silently awards conformance | Resolved (documented) |
| 161 | M25 | the Zoo ships 3 adapters across 3 classes (≥2 required at v0.1.0) | Low | six classes land by v0.2 without changing the adapter shape | Resolved (scoped) |
| 162 | M25 | `HeadToHead.composite_score` is typed `None` and `rank_defenses` always raises | Low | the type system and the API both forbid a composite/ranking | Resolved (design intent) |
| 163 | M25 | `build_head_to_head` shares one `pack_ref` + `seeds` list across cells | Low | identical input is structural, not a convention | Resolved (design intent) |
| 164 | M25 | `require_neutrality` checks published + pre-registered + equal rules | Low | right-of-reply and counsel sign-off are process docs (25.5) | Resolved (documented) |
| 165 | M25 | `author_review_needed` is set-intersection on authors × reviewers | Low | overlap ⇒ independent review required | Resolved (documented) |

| 166 | M26 | SARIF is validated against the vendored **official OASIS schema**; OCSF/OSCAL/STIX validators enforce required fields/enums (full official schemas not vendored) | Medium | schema-validity is full for SARIF; the rest is a documented, tracked follow-up (the OCSF registry is impractical to vendor) | Resolved (documented) |
| 167 | M26 | `findings_from_report` raises on an outcome outside `blocked/missed/degraded/untested` | Low | an unknown result is never silently coerced | Resolved (documented) |
| 168 | M26 | SARIF `suppressions` / OCSF `Suppressed` read the minimal `WaiverRecord` seam, not the M28 ledger | Medium | waivers suppress a gate, never relabel a miss; M28 re-points the seam (no parallel registry) | Resolved (SSOT seam) |
| 169 | M26 | OTel emit/read reuses the ported `OpenTelemetryTracer`; no second tracer | Low | the emitter only maps the drill model onto the existing tracer (SSOT) | Resolved (SSOT) |
| 170 | M26 | 26.4/26.6/26.7 use an injected `Transport`/`SiemQuery`; no network client or credential store in the library | Low | offline-testable; tokens are per-call and never persisted | Resolved (design intent) |
| 171 | M26 | 26.5 **result** import is a new `importer.py`, distinct from M17's **suite** import | Low | results→findings vs suites→packs; no overlapping registry or drift | Resolved (scoped) |
| 172 | M26 | JUnit maps `missed`→failure **and** `degraded`→failure (the WBS names only `missed`) | Low | a partial/un-blocked result must never pass CI unnoticed | Resolved (documented) |
| 173 | M26 | `validate_junit` rejects DTD/entity declarations before parsing | Low | removes the entity-expansion vector on third-party JUnit (S314) | Resolved (hardened) |

| 174 | M27 | Backtest reads the M7 `AgentWatchEvent` stream (SSOT); only `denied` means production blocked | Low | no forked production-event vocabulary | Resolved (SSOT) |
| 175 | M27 | `un_replayable` sessions are itemized and **lower fidelity** (never silently dropped) | High | a backtest on thin data cannot masquerade as complete | Resolved (hardened) |
| 176 | M27 | A **regression** (candidate allows what production denied) dominates a mixed session | Low | the worse security outcome is what surfaces | Resolved (documented) |
| 177 | M27 | Shadow reuses M10 `reporting.ci.bootstrap_ci` for the false-block CI (seeded) | Low | reproducible budget CI; no second stats implementation | Resolved (SSOT) |
| 178 | M27 | Side-effect freedom is proven by an injected M23 witness list, not asserted | Medium | a non-log-only shadow fails the gate | Resolved (design intent) |
| 179 | M27 | Promotion redacts with M18 `lifecycle.privacy` and **refuses** a case with a known secret class | High | zero unredacted secrets is enforced, not assumed | Resolved (hardened) |
| 180 | M27 | Path severity is a **factor rubric, never aggregated**; reachability is structural | Medium | no org-wide composite; `proven_broken` requires drill proof | Resolved (documented) |
| 181 | M27 | Intake drafts only from **cited** facts; the dual-use screen flags off-inventory/uncited steps | High | cite-or-drop and no payload invention beyond the source | Resolved (hardened) |

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
