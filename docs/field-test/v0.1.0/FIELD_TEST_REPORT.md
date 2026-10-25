# agentdrill v0.1.0 — Field Test Report

> **Generated:** — **🚧 not yet run.** This template is filled as the M31 run executes
> ([milestone 24](https://github.com/agentic-suite/agentsec-agentdrill/milestone/24)); every count below is a
> placeholder, re-derived from `field/results/index.jsonl` + the Track A/C suite artifacts — never from a stale
> summary.
> **Overall:** `_pending_` — **_X_ PASS · _Y_ FAIL · _Z_ not run · _W_ N/A** over the 73 v0.1.0 field units
> (Track A 14 · required demonstrations 4 · Track B 19 · Track C 5 · FT-E enrichment 31). Of the PASSes, _G_ are
> **grounded** (an asserting check); blocked/declared/N-A cases are **named**, never faked.
> **Structure:** follows the format of the agentwatch v0.2.0 `FIELD_TEST_REPORT.md` (sister project — a journal,
> not a scoreboard), pointed at [field-test-plan.md](field-test-plan.md) §8 success measures and the §9 exit gate.
> This report states **honestly** what was tested, what passed, what failed, and what was **not** tested.

---

## BLUF + Release Gate Verdict

> **To be written after the run** — the one-paragraph honest verdict: totals, grounded count, defects found and
> fixed, every blocked/declared/N-A case by name, and what the run proved about the harness. A green run without
> the §8 numbers is an unmeasured run.

### Run status (all suites run once; to be filled)

| | Count |
|---|---|
| PASS (raw verdict) | _pending_ |
| — of which grounded (asserting check, not exit-0) | _pending_ |
| — of which NOT grounded (blocked in this environment) | _pending_ |
| FAIL | _pending_ |
| not run (declared, with a named reason) | _pending_ |
| N/A (unsupported/retired — never run) | _pending_ |

### Release gate verdict (computed from run verdicts against the plan §8 success measures)

| # | Gate | Source | Status | Evidence / honesty |
|---|---|---|---|---|
| 1 | CUJ-1..63 exercised end to end (63/63) | plan §8.1 | _pending_ | per-CUJ table below |
| 2 | Track A suites green (14/14) | §8.1 | _pending_ | suite logs + artifacts |
| 3 | Track B matrix: 19/19 agents × configured packs; skip = failure | §8.1 | _pending_ | `field/results/index.jsonl` |
| 4 | Track C infra suites green on the field machine (5/5) | §8.1 | _pending_ | pytest output |
| 5 | Required demonstrations recorded (4/4) | §8.1 / §4.4 | _pending_ | evidence refs |
| 6 | P0 enrichment suites green before the report (8/8) | §8.1 / §4.6 | _pending_ | suite results |
| 7 | 100% of planned scenarios pass after defect fixes (31.5) | §8.2 | _pending_ | `run.json` / `summary.json` |
| 8 | First run ≤ 15 min on a clean machine, zero code changes (CUJ-24) | §8.2 | _pending_ | timed run log |
| 9 | Framework compatibility row: `field-smoke` green on 8/8 frameworks (or misses stated) | §8.2 | _pending_ | compatibility table |
| 10 | Determinism A/B: 100% deterministic-metric identity (FT-E05) | §8.3 | _pending_ | A/B artifacts |
| 11 | Judge credibility published with CIs; zero `judge_drift` (FT-E06) | §8.3 | _pending_ | calibration output |
| 12 | Fail-closed rate 100% on planted faults (FT-E07) | §8.3 | _pending_ | fault log |
| 13 | Scoring-theater plants caught 100% (FT-E21) | §8.3 | _pending_ | meta-verification output |
| 14 | Publish-gate honesty: 100% of bad-number plants rejected (FT-E22) | §8.3 | _pending_ | gate output |
| 15 | Secret-leak sweep: 0 findings beyond the dummy key (FT-E08) | §8.3 | _pending_ | sweep report |
| 16 | Evidence completeness 100% (FT-E20) | §8.3 | _pending_ | evidence audit |
| 17 | Nightly job scheduled + green (FT-E14/E27) | §8.5 | _pending_ | CI history |
| 18 | Report published with the not-tested list — 100% with reasons | §8.1/§8.6 | _pending_ | this document |

## Environment

| Item | Value |
|---|---|
| Host | _pending_ (plan: Apple Silicon macOS) |
| Docker | _pending_ (daemon; images `agentdrill:field` + `agentdrill-agent-runner` built) |
| oMLX endpoint | `http://127.0.0.1:8000/v1` (host) · `http://host.docker.internal:8000/v1` (containers) |
| oMLX model (agents) | `Qwen3.5-4B-4bit` (plan default) — actual: _pending_ |
| Judge model / provider | _pending_ (plan default: same oMLX endpoint; `AGENTDRILL_FIELD_JUDGE_*` recorded per run) |
| Tier(s) run | _pending_ (`local` default; `cheap` cross-check optional) |
| Agents under test | 19 clones at pinned SHAs under `field/agents/` — SHAs _pending_ (precondition §4.5.1) |
| RoE | _pending_ (signed — required before any Wave-0 firing, plan §4.1) |
| Results | `field/results/` (+ Track A/C artifacts under `.agentdrill/runs/` and suite logs) |

## What Was Tested

> **To be filled:** one prose line per track — which suites ran and on what stack/tier, which were re-run after
> fixes, and the honest totals. Include the enrichment cadence actually used (P0 at report time; P1 nightly; P2
> scheduled).

**Status vocabulary (as you fill):** **PASS | FAIL | not run (declared) | N/A** — plus the journal qualifiers:
**✓ grounded** (an asserting check backs the verdict) · **HARDENED** (a weak assertion strengthened and re-run
green) · **FIXED** (a first-pass failure, fixed, re-run green) · **⛔ blocked** (needs tooling absent here — never
faked) · **DECLARED** (not run, with a named reason). A PASS that is not grounded is **⚠ over-claimed** and is
treated as not proven until hardened.

**Class vocabulary:** **P/F** = a hard pass/fail gate · **P/F\|D** = pass/fail-or-declare (a named declaration is
acceptable when the environment cannot provide — never a silent skip).

## Scenario Results (Master Table)

> One row per field unit. Totals are re-derived from `field/results/index.jsonl` + the suite verdicts — a skip is
> a failure; a quarantined agent fails closed (plan §4.2).

### Track A — CUJ end-to-end suites (14)

| Case | Suite | Class | Status | Notes |
|---|---|---|---|---|
| FT-A-QUICKSTART | track-a | P/F | _pending_ | CUJ-24; timed ≤ 15 min on a clean env |
| FT-A-CORE | track-a | P/F\|D | _pending_ | CUJ-1..4; demo + Wave-0 (declare if Wave-0 absent) |
| FT-A-KILLCHAIN | track-a | P/F\|D | _pending_ | CUJ-5/16; kill-time to probed cessation; Wave-0 only |
| FT-A-SELF | track-a | P/F | _pending_ | CUJ-6/25/26/27 + dark holdout |
| FT-A-LIFECYCLE | track-a | P/F | _pending_ | CUJ-7/8/20/21/22 |
| FT-A-TRUST | track-a | P/F | _pending_ | CUJ-11/13/14/15/17/19 |
| FT-A-SCALE | track-a | P/F | _pending_ | CUJ-9/10/12/18 |
| FT-A-VERIFY-OFFLINE | track-a | P/F | _pending_ | CUJ-23 (+11); precondition: verify CLI wiring (§4.5.8) |
| FT-A-ADD-PROOF | track-a | P/F\|D | _pending_ | CUJ-28..31; witness demonstrations D-2/D-3 |
| FT-A-ADD-LAB | track-a | P/F | _pending_ | CUJ-32..35 |
| FT-A-ADD-NEUTRAL | track-a | P/F\|D | _pending_ | CUJ-36/37/54/55; BYOD stack |
| FT-A-ADD-GOV | track-a | P/F\|D | _pending_ | CUJ-38..49; RoE abort demonstration D-4; Wave-0 |
| FT-A-ADD-DETONATE | track-a | P/F | _pending_ | CUJ-50..53/56/57 |
| FT-A-ADD-PLATFORM | track-a | P/F | _pending_ | CUJ-58..63 |

### Required demonstrations (4 — WBS part 17)

| Case | Suite | Class | Status | Notes |
|---|---|---|---|---|
| FT-D-1 verifier-offline | demos | P/F | _pending_ | verifier on a clean machine that never ran the drill |
| FT-D-2 witness-missed | demos | P/F\|D | _pending_ | a witness-confirmed `missed` |
| FT-D-3 witness-discrepancy | demos | P/F\|D | _pending_ | a `witness_discrepancy` (the log lied) |
| FT-D-4 roe-abort | demos | P/F\|D | _pending_ | the RoE abort, in seconds |

### Track B — agent-harness field matrix (19)

| Case | Suite | Class | Status | Notes |
|---|---|---|---|---|
| FT-B-LG-AZURE | track-b | P/F | _pending_ | langgraph · `langgraph-core` + `shared-safety` · min 0.5 |
| FT-B-LG-OFFICIAL | track-b | P/F | _pending_ | langgraph · same packs · min 0.5 |
| FT-B-PAI-AZURE | track-b | P/F | _pending_ | pydantic-ai · `pydantic-ai-core` + `shared-safety` · min 0.5 |
| FT-B-PAI-OFFICIAL | track-b | P/F | _pending_ | pydantic-ai · same packs · min 0.5 |
| FT-B-CREW-QUICKSTARTS | track-b | P/F | _pending_ | crewai · `crewai-core` + `shared-safety` · min 0.5 |
| FT-B-CREW-EXAMPLES | track-b | P/F | _pending_ | crewai · same packs · min 0.5 |
| FT-B-CREW-QS | track-b | P/F | _pending_ | crewai · same packs · min 0.5 |
| FT-B-OA-AZURE | track-b | P/F | _pending_ | openai-agents · `openai-agents-core` + `shared-safety` · min 0.5 |
| FT-B-OA-OFFICIAL | track-b | P/F | _pending_ | openai-agents · same packs · min 0.5 |
| FT-B-SM-QS | track-b | P/F | _pending_ | smolagents · `smolagents-core` + `shared-safety` · min 0.5 |
| FT-B-SM-SMOLCC | track-b | P/F | _pending_ | smolagents · same packs · min 0.5 |
| FT-B-SM-DEEPSEARCH | track-b | P/F | _pending_ | smolagents · same packs · min 0.5 |
| FT-B-AG-AZURE | track-b | P/F | _pending_ | autogen · `autogen-core` + `shared-safety` · min 0.5 |
| FT-B-AG-OFFICIAL | track-b | P/F | _pending_ | autogen · same packs · min 0.5 |
| FT-B-LI-AZURE | track-b | P/F | _pending_ | llamaindex · `llamaindex-core` + `shared-safety` · min 0.5 |
| FT-B-LI-OFFICIAL | track-b | P/F | _pending_ | llamaindex · same packs · min 0.5 |
| FT-B-ADK-QS | track-b | P/F | _pending_ | adk · `adk-core` + `shared-safety` · min 0.5 |
| FT-B-ADK-SOKART | track-b | P/F | _pending_ | adk · same packs · min 0.5 |
| FT-B-ADK-OFFICIAL | track-b | P/F | _pending_ | adk · same packs · min 0.5 |

Per-scenario verdicts live in `field/results/tests/<agent>/<scenario>/<tier>__<model>/result.json`; the counts
below are the per-agent rollup.

### Track C — docker / LLM infrastructure suites (5)

| Case | Suite | Class | Status | Notes |
|---|---|---|---|---|
| FT-C-IMAGE | track-c | P/F | _pending_ | `tests/test_docker.py` (-m docker): image builds, CLI in-container |
| FT-C-CONTAINER-LLM | track-c | P/F | _pending_ | `tests/test_security_docker_llm.py`: container → oMLX via `host.docker.internal` |
| FT-C-SANDBOX | track-c | P/F | _pending_ | `tests/test_security_container_integration.py`: `run_in_container` paths |
| FT-C-JUDGE | track-c | P/F | _pending_ | `tests/test_judge_omlx_integration.py` (-m omlx): real verdicts, pinned model |
| FT-C-ADAPTERS | track-c | P/F | _pending_ | `tests/test_adapters_{adk,autogen,llamaindex,smolagents}_llm.py` (-m omlx) |

### FT-E enrichment (31 — P0 gates the report; P1 nightly; P2 scheduled)

| Case | Suite | Class | Status | Notes |
|---|---|---|---|---|
| FT-E01 metric-coverage | ft-e-p0 | P/F | _pending_ | field packs exercise the full 31-scorer registry |
| FT-E02 security-eval-pack | ft-e-p0 | P/F | _pending_ | injection/exfil/SSRF/sandbox-escape scorers in the field |
| FT-E05 determinism-ab | ft-e-p0 | P/F | _pending_ | repeat run: deterministic metrics identical |
| FT-E06 judge-credibility | ft-e-p0 | P/F | _pending_ | battery + canaries + CIs vs the pinned local judge |
| FT-E07 fault-injection | ft-e-p0 | P/F | _pending_ | fail-closed + exit codes on planted faults |
| FT-E08 secret-leak-sweep | ft-e-p0 | P/F | _pending_ | 0 findings across all artifacts |
| FT-E21 meta-verification | ft-e-p0 | P/F | _pending_ | scoring-theater plants all caught |
| FT-E22 publish-gate-honesty | ft-e-p0 | P/F | _pending_ | bad-number plants all rejected |
| FT-E03 injection-carriers | ft-e-p1 | P/F | _pending_ | 12 lab carriers through tool results |
| FT-E04 reliability-k | ft-e-p1 | P/F | _pending_ | `Hold@k`/`ASR@k`, k ∈ {5,25} |
| FT-E09 efficacy-control | ft-e-p1 | P/F | _pending_ | unguarded twins; `attack_inert` flagged |
| FT-E10 utility-under-attack | ft-e-p1 | P/F | _pending_ | benign twins; three-metric frame |
| FT-E11 baseline-drift | ft-e-p1 | P/F | _pending_ | baselines + comparison + change detection |
| FT-E12 schema-verifier | ft-e-p1 | P/F | _pending_ | artifact schema validation + offline verify |
| FT-E13 dark-holdout | ft-e-p1 | P/F | _pending_ | unpublished subset; pack-gaming finding |
| FT-E14 nightly-canary-trend | ft-e-p1 | P/F | _pending_ | driver canary + "what got worse" |
| FT-E23 sandbox-egress | ft-e-p1 | P/F | _pending_ | 0 non-loopback contact, capture-verified |
| FT-E24 parallel-equals-serial | ft-e-p1 | P/F | _pending_ | `--workers N` == serial, order preserved |
| FT-E25 cross-os-parity | ft-e-p1 | P/F\|D | _pending_ | ≥ 99.5% parity vs the Linux container variant |
| FT-E26 interop-import | ft-e-p1 | P/F\|D | _pending_ | real promptfoo/garak/AgentDojo/PyRIT suite end-to-end |
| FT-E27 release-shape-gates | ft-e-p1 | P/F | _pending_ | parity gate, claims linter, drift watcher, self-attack cadence |
| FT-E28 dryrun-mcp-readonly | ft-e-p1 | P/F | _pending_ | 0 executions; no write tools (needs §4.5.9 wiring) |
| FT-E15 cost-governor | ft-e-p2 | P/F | _pending_ | over-budget ⇒ loud `cost_exceeded` |
| FT-E16 timeout-probing | ft-e-p2 | P/F | _pending_ | timeout-enforcement p50/p95, ≥5 trials |
| FT-E17 multiagent-approval | ft-e-p2 | P/F | _pending_ | delegation + approval fidelity (partial, labeled) |
| FT-E18 model-matrix | ft-e-p2 | P/F | _pending_ | ≥3 models × representative agents |
| FT-E19 vcr-record-replay | ft-e-p2 | P/F | _pending_ | cassette replay scores identically, fully offline |
| FT-E20 evidence-completeness | ft-e-p2 | P/F | _pending_ | every result carries its full evidence chain |
| FT-E29 judge-backend-parity | ft-e-p2 | P/F | _pending_ | oMLX vs Ollama vs MLXJudgeClient verdicts agree |
| FT-E30 judge-cache-correctness | ft-e-p2 | P/F | _pending_ | cache hit never changes a verdict |
| FT-E31 plugin-discovery | ft-e-p2 | P/F | _pending_ | entry-point discovery + loud unknown-metric failure |

**Totals:** _pending_ — _X_ PASS · _Y_ FAIL · _Z_ not run · _W_ N/A (of 73 v0.1.0 field units).

## Track B Matrix (per-agent rollup placeholders)

Filled per sweep from `field/results/`: `index.jsonl` (per-scenario verdicts) → per-agent counts → pass rate
vs the config's `minimum_pass_rate` (0.5). Judge tier and model are recorded per run; **skip = failure**.

| Agent | Framework | Packs (config) | Tier(s) run | Scenarios | PASS | FAIL | not run | N/A | Pass rate | ≥ 0.5 |
|---|---|---|---|---|---|---|---|---|---|---|
| lg-azure | langgraph | langgraph-core, shared-safety | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| lg-official | langgraph | langgraph-core, shared-safety | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| pai-azure | pydantic-ai | pydantic-ai-core, shared-safety | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| pai-official | pydantic-ai | pydantic-ai-core, shared-safety | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| crew-quickstarts | crewai | crewai-core, shared-safety | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| crew-examples | crewai | crewai-core, shared-safety | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| crew-qs | crewai | crewai-core, shared-safety | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| oa-azure | openai-agents | openai-agents-core, shared-safety | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| oa-official | openai-agents | openai-agents-core, shared-safety | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| sm-qs | smolagents | smolagents-core, shared-safety | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| sm-smolcc | smolagents | smolagents-core, shared-safety | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| sm-deepsearch | smolagents | smolagents-core, shared-safety | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| ag-azure | autogen | autogen-core, shared-safety | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| ag-official | autogen | autogen-core, shared-safety | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| li-azure | llamaindex | llamaindex-core, shared-safety | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| li-official | llamaindex | llamaindex-core, shared-safety | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| adk-qs | adk | adk-core, shared-safety | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| adk-sokart | adk | adk-core, shared-safety | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |
| adk-official | adk | adk-core, shared-safety | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ | _pending_ |

## Per-Suite Results

### track-a — 14 case(s)

_pending_ — _X_ PASS · _Y_ FAIL · _Z_ not run · _W_ N/A

### demos — 4 case(s)

_pending_ — _X_ PASS · _Y_ FAIL · _Z_ not run · _W_ N/A

### track-b — 19 case(s) (agent × configured packs; per-scenario verdicts in `index.jsonl`)

_pending_ — _X_ PASS · _Y_ FAIL · _Z_ not run · _W_ N/A

### track-c — 5 case(s)

_pending_ — _X_ PASS · _Y_ FAIL · _Z_ not run · _W_ N/A

### ft-e-p0 — 8 case(s) (gate the report)

_pending_ — _X_ PASS · _Y_ FAIL · _Z_ not run · _W_ N/A

### ft-e-p1 — 14 case(s) (nightly cadence)

_pending_ — _X_ PASS · _Y_ FAIL · _Z_ not run · _W_ N/A

### ft-e-p2 — 9 case(s) (scheduled behind P1)

_pending_ — _X_ PASS · _Y_ FAIL · _Z_ not run · _W_ N/A

## CUJ-1..63 Verification

A CUJ is ✅ only if every proving case passed; ◑ if some did. Proving suites are from the plan §4.1 mapping.

| CUJ | Proving cases (status) | Verdict |
|---|---|---|
| CUJ-1 | FT-A-CORE (_pending_) | _pending_ |
| CUJ-2 | FT-A-CORE (_pending_) | _pending_ |
| CUJ-3 | FT-A-CORE (_pending_) | _pending_ |
| CUJ-4 | FT-A-CORE (_pending_) | _pending_ |
| CUJ-5 | FT-A-KILLCHAIN (_pending_) | _pending_ |
| CUJ-6 | FT-A-SELF (_pending_) | _pending_ |
| CUJ-7 | FT-A-LIFECYCLE (_pending_) | _pending_ |
| CUJ-8 | FT-A-LIFECYCLE (_pending_) | _pending_ |
| CUJ-9 | FT-A-SCALE (_pending_) | _pending_ |
| CUJ-10 | FT-A-SCALE (_pending_) | _pending_ |
| CUJ-11 | FT-A-TRUST (_pending_), FT-A-VERIFY-OFFLINE (_pending_) | _pending_ |
| CUJ-12 | FT-A-SCALE (_pending_) | _pending_ |
| CUJ-13 | FT-A-TRUST (_pending_) | _pending_ |
| CUJ-14 | FT-A-TRUST (_pending_) | _pending_ |
| CUJ-15 | FT-A-TRUST (_pending_) | _pending_ |
| CUJ-16 | FT-A-KILLCHAIN (_pending_) | _pending_ |
| CUJ-17 | FT-A-TRUST (_pending_) | _pending_ |
| CUJ-18 | FT-A-SCALE (_pending_) | _pending_ |
| CUJ-19 | FT-A-TRUST (_pending_) | _pending_ |
| CUJ-20 | FT-A-LIFECYCLE (_pending_) | _pending_ |
| CUJ-21 | FT-A-LIFECYCLE (_pending_) | _pending_ |
| CUJ-22 | FT-A-LIFECYCLE (_pending_) | _pending_ |
| CUJ-23 | FT-A-VERIFY-OFFLINE (_pending_) | _pending_ |
| CUJ-24 | FT-A-QUICKSTART (_pending_) | _pending_ |
| CUJ-25 | FT-A-SELF (_pending_) | _pending_ |
| CUJ-26 | FT-A-SELF (_pending_) | _pending_ |
| CUJ-27 | FT-A-SELF (_pending_) | _pending_ |
| CUJ-28 | FT-A-ADD-PROOF (_pending_) | _pending_ |
| CUJ-29 | FT-A-ADD-PROOF (_pending_) | _pending_ |
| CUJ-30 | FT-A-ADD-PROOF (_pending_) | _pending_ |
| CUJ-31 | FT-A-ADD-PROOF (_pending_) | _pending_ |
| CUJ-32 | FT-A-ADD-LAB (_pending_) | _pending_ |
| CUJ-33 | FT-A-ADD-LAB (_pending_) | _pending_ |
| CUJ-34 | FT-A-ADD-LAB (_pending_) | _pending_ |
| CUJ-35 | FT-A-ADD-LAB (_pending_) | _pending_ |
| CUJ-36 | FT-A-ADD-NEUTRAL (_pending_) | _pending_ |
| CUJ-37 | FT-A-ADD-NEUTRAL (_pending_) | _pending_ |
| CUJ-38 | FT-A-ADD-GOV (_pending_) | _pending_ |
| CUJ-39 | FT-A-ADD-GOV (_pending_) | _pending_ |
| CUJ-40 | FT-A-ADD-GOV (_pending_) | _pending_ |
| CUJ-41 | FT-A-ADD-GOV (_pending_) | _pending_ |
| CUJ-42 | FT-A-ADD-GOV (_pending_) | _pending_ |
| CUJ-43 | FT-A-ADD-GOV (_pending_) | _pending_ |
| CUJ-44 | FT-A-ADD-GOV (_pending_) | _pending_ |
| CUJ-45 | FT-A-ADD-GOV (_pending_) | _pending_ |
| CUJ-46 | FT-A-ADD-GOV (_pending_) | _pending_ |
| CUJ-47 | FT-A-ADD-GOV (_pending_) | _pending_ |
| CUJ-48 | FT-A-ADD-GOV (_pending_) | _pending_ |
| CUJ-49 | FT-A-ADD-GOV (_pending_) | _pending_ |
| CUJ-50 | FT-A-ADD-DETONATE (_pending_) | _pending_ |
| CUJ-51 | FT-A-ADD-DETONATE (_pending_) | _pending_ |
| CUJ-52 | FT-A-ADD-DETONATE (_pending_) | _pending_ |
| CUJ-53 | FT-A-ADD-DETONATE (_pending_) | _pending_ |
| CUJ-54 | FT-A-ADD-NEUTRAL (_pending_) | _pending_ |
| CUJ-55 | FT-A-ADD-NEUTRAL (_pending_) | _pending_ |
| CUJ-56 | FT-A-ADD-DETONATE (_pending_) | _pending_ |
| CUJ-57 | FT-A-ADD-DETONATE (_pending_) | _pending_ |
| CUJ-58 | FT-A-ADD-PLATFORM (_pending_) | _pending_ |
| CUJ-59 | FT-A-ADD-PLATFORM (_pending_) | _pending_ |
| CUJ-60 | FT-A-ADD-PLATFORM (_pending_) | _pending_ |
| CUJ-61 | FT-A-ADD-PLATFORM (_pending_) | _pending_ |
| CUJ-62 | FT-A-ADD-PLATFORM (_pending_) | _pending_ |
| CUJ-63 | FT-A-ADD-PLATFORM (_pending_) | _pending_ |

## Root Cause Analysis

> **To be filled per failure.** Classify every failure per the plan §7 taxonomy — **shim / wrong config /
> adapter / oracle** — name the root cause, the fix, and the confirming re-run. No failure is closed by
> re-running alone.

_pending_ — no run yet.

## Defect Catalogue

Every found defect also lands a linked regression test (plan §7, 31.5). No defect closes without evidence.

| Case | Suite | Failed assertions | Root cause | Fix | Regression test | Evidence |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — |

## Deep Analysis Notes (journal)

This report is a **journal, not a scoreboard**. Per batch, this section records **what each case actually
proved** — the assertion the step ran, the evidence left on disk, and any gap between that assertion and the
plan's pass condition ([field-test-plan.md](field-test-plan.md) §4). **"Assertion ran" ≠ "condition proved."**

Method per case: read the generated step, read the driver it invokes, read the captured
`console.log`/`result.json`/`llm/` captures, and compare against the plan's condition. An entry marked
**⚠ OVER-CLAIMED** is a PASS whose assertion does not establish the plan's condition — treat it as **not proven
(effectively failing)** until the step is hardened. An entry marked **✓ GROUNDED** is genuinely backed by
evidence.

### Batch logs

> One subsection per run batch: run log path, verdicts, and the per-case table
> `| Case | Verdict | What the step actually asserted | Gap vs the plan condition | Call |` plus per-case
> evidence notes. Record harness noise and every fix; a fix is only real when re-run green.

_pending_ — no batches run yet.

### Hardening backlog — every PASS

Status: **G** grounded · **R** run-only · **V** vacuous. Every PASS must be grounded or explicitly blocked.

| Suite | Case | Now (G/R/V) | Hardening needed |
|---|---|---|---|
| — | — | — | — |

### Hardening progress log

| Case | New assertion | Result |
|---|---|---|
| — | — | — |

## Issues Found & Fixed During Validation

> Numbered (F-1, F-2, …), newest last; classify each as **harness** or **product** — keep the classes honest
> (plan §7).

_pending_ — none yet.

## Observations — themes fixed, what worked, what didn't

### Themes of issues fixed

_pending_

### What worked

_pending_

### What didn't work (and what we did about it)

_pending_

### Harness vs product

> The split that keeps the count honest: which failures were harness wiring vs real product defects, and what
> hardening surfaced.

_pending_

## Learnings

> Numbered, one line each — seed from the run (the agentwatch v0.2.0 learnings list is the house style).

_pending_

## Takeaways

_pending_

## Deferred Items (pre-run preconditions — plan §4.5)

Each precondition must close before its suite runs, or the suite **declares** (never silently skips). Track
disposition here.

| # | Item (plan §4.5) | Blocks | Disposition |
|---|---|---|---|
| 1 | Pin the 19 agent SHAs (`field/list.txt` all `TODO`) | Track B determinism; FT-E11 | _pending_ |
| 2 | `field/setup.sh` default list points at nonexistent `field/list1.txt` | Track B setup | _pending_ |
| 3 | Runtime image bakes only `scenarios/` — `packs/` + `field/` not in image | in-container demo/quickstart (§5.6/5.7) | _pending_ |
| 4 | Image extras partial (`[dev,judge,langgraph,pydanticai]`) | in-container matrix variants | _pending_ |
| 5 | macOS-built agent venvs cannot run in Linux containers | FT-E25; §5.7 variant | _pending_ |
| 6 | Dockerfile label/license mismatch (MIT vs Apache-2.0) | release scans (M32) | _pending_ |
| 7 | Nightly CI runner choice (no MLX on hosted runners) | FT-E14; §5.9 | _pending_ |
| 8 | `agentdrill verify` CLI is a planned stub | FT-A-VERIFY-OFFLINE; FT-D-1; FT-E12 | _pending_ |
| 9 | `agentdrill run --dry-run`/`--explain` documented but unwired | FT-E28 | _pending_ |
| 10 | Optional minimal `docker compose` (agentdrill + Ollama sidecar) | one-command env | _pending_ |

## Coverage, Gaps, and Declared Limitations

Status vocabulary: **not run | PASS | FAIL | N/A** — this run: `_pending_`.

- **Coverage:** _pending_ — which of the 73 field units ran, and how many PASSes are grounded.
- **Gaps:** _pending_ — hardenable cases that remain, and why.
- **Not tested (honest — mandatory, with reasons):**
  - _pending_ (environments, harnesses, surfaces, tiers not exercised — filled at run time)
  - Known up front, by design (plan §4.6 boundary): browser/computer-use frontier classes (no browser-wired
    field agent); T3 adaptive search (DD-44 deferred); third-party SaaS platforms (out of v0.1.0 scope).
- A measure not taken is a not-tested entry, never a silent omission (plan §8.6).

## Success Metrics (targets from the plan §8; Achieved filled at run time)

### 8.1 Coverage

| Measure | Target | Achieved | Evidence |
|---|---|---|---|
| CUJs exercised end to end | 63/63 | _pending_ | per-CUJ table |
| Track A suites executed | 14/14 | _pending_ | suite logs + artifacts |
| Track B matrix | 19/19 agents × configured packs (skip = failure) | _pending_ | `index.jsonl` |
| Track C infra suites green | 5/5 | _pending_ | pytest output |
| Required demonstrations recorded | 4/4 | _pending_ | §4.4 evidence refs |
| Enrichment suites | P0 8/8 before the report; P1 nightly; P2 scheduled | _pending_ | §4.6 results |
| Agent SHA pinning | 100% | _pending_ | clone log |
| Not-tested list completeness | 100% with reasons | _pending_ | this report |

### 8.2 Outcomes

| Measure | Target | Achieved | Evidence |
|---|---|---|---|
| Scenario pass rate (milestone bar) | 100% after defect fixes | _pending_ | `run.json`/`summary.json` |
| Per-agent acceptance (triage bar) | ≥ `minimum_pass_rate` (0.5) each | _pending_ | per-agent rollup |
| Skip/quarantine discipline | every skip = failure with reason | _pending_ | `index.jsonl` |
| Exit codes | 0 green; non-zero classified (§5.8) | _pending_ | suite exit codes |
| Defect closure | 100% fixed with a linked regression test | _pending_ | defects table |
| Framework compatibility row | `field-smoke` green 8/8 (or misses stated) | _pending_ | compatibility table |
| First-run (CUJ-24) | ≤ 15 min, zero code changes | _pending_ | timed run log |

### 8.3 Trust

| Measure | Target | Achieved | Evidence |
|---|---|---|---|
| Determinism A/B (FT-E05) | 100% deterministic-metric identity | _pending_ | A/B artifacts |
| Judge credibility (FT-E06) | rates with CIs; zero `judge_drift` | _pending_ | calibration output |
| Judge non-mock guard | 100% provider ≠ `mock` + evidence files | _pending_ | `test_field_agent.py` §5a |
| Fail-closed rate (FT-E07) | 100%, right exit codes, zero silent greens | _pending_ | fault log |
| Theater plants caught (FT-E21) | 100% | _pending_ | meta-verification output |
| Publish-gate honesty (FT-E22) | 100% of bad-number plants rejected | _pending_ | gate output |
| Secret-leak sweep (FT-E08) | 0 findings beyond dummy `omlx-test` | _pending_ | sweep report |
| Evidence completeness (FT-E20) | 100% carry the full chain | _pending_ | evidence audit |

### 8.4 Reliability & stability

| Measure | Target | Achieved | Evidence |
|---|---|---|---|
| Repeated-trial stability (FT-E04) | holds across k ∈ {5,25} within the flake budget | _pending_ | `Hold@k`/`ASR@k` |
| Timeout discipline | ≤ 30 s/scenario (local); every timeout a failure | _pending_ | `result.json` durations |
| Parallel == serial (FT-E24) | identical outcomes, order preserved | _pending_ | comparison output |
| Cross-OS parity (FT-E25, if run) | ≥ 99.5% | _pending_ | parity report |
| Judge/cache correctness (FT-E29/E30) | identical verdicts; cache never changes one | _pending_ | battery + `cache_stats` |
| Baseline drift (FT-E11) | regressions flagged within one nightly | _pending_ | comparison/trend output |
| Egress containment (FT-E23) | 0 non-loopback contact | _pending_ | network capture + audit |

### 8.5 Efficiency, cost & cadence

| Measure | Target | Achieved | Evidence |
|---|---|---|---|
| Local-tier cost | $0.00; cloud within `--max-cost` | _pending_ | cost report |
| Cost-governor (FT-E15) | over-budget ⇒ loud `cost_exceeded` | _pending_ | governor log |
| Suite duration | within per-tier ceilings (5/10/15 min) | _pending_ | run timings |
| Cache savings | reported per sweep, provenance labeled | _pending_ | `cache_stats` |
| Nightly job (FT-E14/E27) | scheduled + green; release-shape gates green | _pending_ | CI history |

## Claims Ledger + Known-Limitations Shrink Evidence

> Gate: FT-E27 (claims linter zero violations; every published number has a ledger entry).
> [known-limitations.md](../../reference/known-limitations.md) is updated in the same pass (31.D, issue #91).

_pending_

## Certification / Standards Conformance

| Framework | Case | Status |
|---|---|---|
| MITRE ATLAS + OWASP LLM/Agentic tagging on every pack | FT-A-LIFECYCLE, FT-A-ADD-PLATFORM (CUJ-63) | _pending_ |
| SARIF / JUnit / OSCAL / OTel / OCSF / STIX conformance | FT-E12, FT-A-ADD-NEUTRAL | _pending_ |
| Evidence indexes with explicit `not covered` (CUJ-62) | FT-A-ADD-PLATFORM | _pending_ |
| Release-shape gates (parity, claims, drift, cadence) | FT-E27 | _pending_ |

## Performance & Timings

| Measure | Target | Achieved |
|---|---|---|
| First-run (quickstart, CUJ-24) | ≤ 15 min | _pending_ |
| Per-scenario duration (local tier) | ≤ 30 s | _pending_ |
| Suite duration per tier | local 5 min · cheap 10 min · better 15 min | _pending_ |
| Kill-time per stage (FT-A-KILLCHAIN) | p50/p95/max, ≥5 trials | _pending_ |
| Timeout-enforcement latency (FT-E16) | p50/p95, ≥5 trials | _pending_ |
| Judge cache savings | reported, provenance labeled | _pending_ |

## Results & Coverage Comparison

First field report for agentdrill — no prior version; this run is the **baseline** for future releases.

| | Plan (v0.1.0) | This run |
|---|---|---|
| Field units | 73 (A 14 · D 4 · B 19 · C 5 · E 31) | _pending_ |
| CUJs exercised | 63/63 | _pending_ |
| P0 enrichment green | 8/8 | _pending_ |

## Action Items

Pre-run (from the plan §5 runbook, in order):

1. [ ] Close the §4.5 preconditions (Deferred Items table above) — at minimum #1, #2, #8, #9 before their suites.
2. [ ] Preflight: `docker info` + oMLX `/v1/models` + `uv run agentdrill doctor`.
3. [ ] Build images: `agentdrill:field` + `agentdrill-agent-runner` (§5.1).
4. [ ] Layers 1–2: docker/omlx-marked suites green on the field machine (§5.2–5.3).
5. [ ] Layer 3: `bash field/setup.sh` → `run-local.sh --tier local --dry-run` → one agent → full matrix (§5.4).
6. [ ] P0 enrichment (E01, E02, E05–E08, E21, E22) before the report is filled.
7. [ ] Fill this report top-down; re-derive all counts from `field/results/index.jsonl` + suite verdicts.

Run-derived action items:

_pending_

## Reproducibility / Evidence Paths

Per scenario: `field/results/tests/<agent>/<scenario>/<tier>__<model>/` with `result.json`, `console.log`,
`agentdrill/{artifact.json, prompt.txt, completion.txt, trajectory.jsonl, llm/*-request|response.json}`,
`score-<scenario>.json`, `judge/<scenario>/{<metric>-prompt.txt, <metric>-verdict.json}`. Track A/C artifacts
under `.agentdrill/runs/<run_id>/`. Everything sanitized before push (secrets masked; agents/ gitignored).

Reproduce (plan §5):

```sh
# Environment
docker info && curl -s http://127.0.0.1:8000/v1/models | head -5
uv run agentdrill doctor

# Layers 1–2
docker build -t agentdrill:field -f Dockerfile .
docker build -t agentdrill-agent-runner -f Dockerfile .
uv run pytest tests/test_docker.py -m docker
uv run pytest tests/test_security_docker_llm.py tests/test_security_container_integration.py -m docker
uv run pytest tests/test_judge_omlx_integration.py -m omlx

# Layer 3 — the agent matrix (local LLM tier)
bash field/setup.sh
bash field/run-local.sh --tier local --dry-run
bash field/run-local.sh --tier local
```

Exit codes (docs/reference/errors.md): `0` pass · `1` misses · `2` config · `3` judge/oracle infra ·
`4` critical miss · `5` critical divergence.

## Appendices

- Plan: [field-test-plan.md](field-test-plan.md) (suites §4, runbook §5, success measures §8, exit gate §9).
- Field workspace: [`field/README.md`](../../field/README.md) (runner controls, results layout).
- CI strategy: [docs/ci-field-tests.md](../../ci-field-tests.md) (tiers, ceilings, flake budget).
- Error contract: [docs/reference/errors.md](../../reference/errors.md).
- Issue tracker: [milestone 24](https://github.com/agentic-suite/agentsec-agentdrill/milestone/24) (#82–#91, #383).
