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
