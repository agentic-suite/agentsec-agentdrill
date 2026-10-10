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
