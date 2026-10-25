# Field-test Docker harness

Harness for the **[Field Test Plan](../../docs/field-test/v0.1.0/field-test-plan.md)**.
Final results are published to
[`docs/field-test/v0.1.0/FIELD_TEST_REPORT.md`](../../docs/field-test/v0.1.0/FIELD_TEST_REPORT.md).

It reuses the repo's stack lifecycle primitive
([`../stack_lib.sh`](../stack_lib.sh)) and adds per-case result capture. Results
land under **`field-test/<FT_VERSION>/results/<run-id>/`** (version-scoped;
`v0.1.0` today).

## Layout

```
scripts/fieldtest/
  docker-compose.fieldtest.yml   the stack: the agentdrill CLI/SDK (no LLM container)
  agentdrill.Dockerfile          agentdrill CLI + SDK image (system under test)
  lib.sh                         ft_* helpers on top of stack_lib.sh
  .env.example                   copy to .env
  gen_cases.py                   source of truth: registry -> specs + steps (+ weak-step guard)
  run-case.sh                    run one case
  run-all.sh                     run every case
  run-suite.sh                   run one suite (track-a, demos, track-b, track-c, ft-e-p0/1/2)
  run-ft-all.sh                  run every suite
  stack-ft.sh                    stack up|down|ps|verify|reset (manual runs)
  collect-results.py             aggregate verdicts -> summary.json/md
  build_report.py                fill FIELD_TEST_REPORT.md sections from the results
  check_grounding.py             deep-verification gate: every PASS must be grounded
  run_pytest.py                  grounded pytest driver (skip = failure)
  run_agent.py                   Track B matrix driver (parses the runner summary, captures LLM)
  llm_capture.py                 make one real LLM call + record the request/response pair
  _ftutil.py                     helpers for in-container drivers
  cases/<ID>-*.md                per-case spec (generated)
  cases/steps/<ID>.sh            per-case runner (generated)
  cases/registry.json            the case list
  fixtures/                      version-tagged fixtures (read-only at runtime)
```

## No skips

Every case runs and is `pass`/`fail`; a case that cannot run (e.g. Docker absent
for a Docker case) is recorded as a **failure** and the suite exits non-zero. A
`P/F|D` case may resolve to `declared` via `ft_declare "<limitation>" "<gate>"`
only where the plan says "or declared"; a `declared` case is recorded distinctly
— **never** as a pass. A hard-gate case can never declare.

## Deep verification (must)

A surface pass ("the command ran") is not a pass. The harness enforces this at
three layers:

1. **`ft_assert` records the *command* and a `grounded` flag** for every
   assertion (`assertions.ndjson`); the weak shapes — import-only,
   existence-only (`test -f/-s`), `json.tool`, `|| true` (cannot-fail), bare
   in-container driver — are marked **not grounded**.
2. **`ft_finalize` fails a PASS with no grounded assertion** (`FT_STRICT_GROUNDING=1`,
   default). A pass backed only by plumbing is a failure, not a green.
3. **`check_grounding.py`** re-derives grounding from the evidence on disk and
   exits non-zero if any PASS is over-claimed.

`run_pytest.py` additionally treats a **skipped** test as a failure, and
`run_agent.py` parses the field runner's `summary.json` (which always exits 0)
so a failed sweep cannot pass.

## LLM request/response capture (must)

Every LLM-required case records the full request/response pair(s) it made, under
`artifacts/llm/` as `<name>-request.json` / `<name>-response.json`, **sanitized**
(secrets masked). An LLM case that captured no pair **fails** (`ft_finalize`).
`llm_capture.py` makes a real call through the pinned endpoint; pytest-driven LLM
cases set `AGENTDRILL_FIELD_OUTPUT_DIR` so the httpx capture lands in the case
artifacts.

## Persisted in git (all runs)

Every run is **committed**: `field-test/<FT_VERSION>/results/<suite>/` (per-case
`verdict.json`, `assertions.ndjson`, `commands.log`, `stdout/stderr.log`, and
`artifacts/` incl. `artifacts/llm/`). Because results are permanent, they must be
**sanitized**:

- `ft_case_end` runs a **leak gate** over each case's `artifacts/` — an unmasked
  secret **fails the case** (`no-secret-leak`), so a leak cannot be committed.
- `scripts/fieldtest/scan_results.py` (`make fieldtest-scan`) is the repo-wide
  gate over the whole results tree.
- `make fieldtest-persist` scans, fills the report, and stages
  `field-test/` + `docs/field-test/` for commit.

## Run

```bash
cp scripts/fieldtest/.env.example scripts/fieldtest/.env
python3 scripts/fieldtest/gen_cases.py          # regenerate specs/steps from the registry
FT_STRICT_STEPS=1 python3 scripts/fieldtest/gen_cases.py   # ...and fail on any weak step

bash scripts/fieldtest/run-ft-all.sh            # every suite
bash scripts/fieldtest/run-suite.sh track-c     # one suite
bash scripts/fieldtest/run-case.sh FT-C-IMAGE   # one case

python3 scripts/fieldtest/collect-results.py    # summary.json/md for the newest run
python3 scripts/fieldtest/check_grounding.py    # deep-verification gate
python3 scripts/fieldtest/build_report.py       # fill FIELD_TEST_REPORT.md
```

## Prerequisites

- Docker daemon + Compose v2 (`docker compose`). Host-native cases (`requires:
  python`) run without Docker.
- For the LLM cases (`requires: ...llm`): the local **oMLX** server on the host
  (`http://127.0.0.1:8000/v1`, OpenAI-compatible; the container reaches it via
  `host.docker.internal:8000`). If the endpoint is unreachable the case **fails**
  (no fake green). There is no Ollama dependency.
- The Track B matrix (`run_agent.py`) additionally needs the third-party agent
  clones (`field/setup.sh`) and their per-agent venvs; see the plan §4.5.

## Environment

| Variable | Meaning |
|---|---|
| `FT_VERSION` | results root (`field-test/<FT_VERSION>/results`); default `v0.1.0` |
| `FT_RESULTS_ROOT` | override the whole results path |
| `FT_RUN_ID` | run directory name (default `all`, or the suite name) |
| `LLM_BASE_URL` / `LLM_MODEL` / `JUDGE_MODEL` | the pinned LLM endpoint + models |
| `FT_STRICT_GROUNDING` | `1` (default): a pass with no grounded assertion fails |
| `FT_STRICT_STEPS` | `1`: `gen_cases.py` fails while any weak step remains |
| `STACK_KEEP` / `STACK_TIMEOUT` | leave the stack up (debug) / per-phase timeout |
| `FT_FROZEN_VERSIONS` | versions that must never be written (freeze guard) |
