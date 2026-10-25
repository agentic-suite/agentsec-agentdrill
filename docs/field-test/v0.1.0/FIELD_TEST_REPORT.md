# agentdrill v0.1.0 — Field Test Report

> **Generated:** 2026-10-25 — **partial run.** The **Track C** (docker/LLM infrastructure) suite has been run and
> **deeply verified**; the remaining 68 field units are not yet run. Counts are re-derived from the committed
> `field-test/v0.1.0/results/` verdicts — never from a stale summary.
> **Overall:** **5 PASS · 0 FAIL · 0 declared · 68 not run** (of 73 v0.1.0 field units). Of the 5 PASS, **5 are
> grounded** (2–4 grounded checks each, 0 skipped / 0 failed per suite) and **every LLM case captured its
> request/response pair** (real 2xx). Nothing is faked; not-run units are stated plainly.
> **Structure:** follows the format of the agentwatch v0.2.0 `FIELD_TEST_REPORT.md` (sister project — a journal,
> not a scoreboard), pointed at [field-test-plan.md](field-test-plan.md) §8 success measures and the §9 exit gate.
> This report states **honestly** what was tested, what passed, what failed, and what was **not** tested.

---

## BLUF + Release Gate Verdict

> **First (partial) run: 5 PASS · 0 FAIL · 0 declared · 68 not run.** The **Track C** docker/LLM infrastructure
> suite — the layer the whole run depends on — is green and **deeply verified**. Each case rests on a real,
> asserting check (not an exit-0): `FT-C-IMAGE` 4 passed/0 skipped, `FT-C-SANDBOX` 6/0, `FT-C-CONTAINER-LLM` 1/0,
> `FT-C-JUDGE` 10/0, `FT-C-ADAPTERS` 8/0. The three LLM cases each captured a real 2xx response
> (`model=Qwen3.5-4B-4bit`, `choices` present, sanitized). The deep-verification gate is green (**5/5 grounded,
> 0 over-claimed**) and the leak gate is clean (**36 files scanned**). **No defects found.** Track A, the four
> required demonstrations, Track B, and the 31 FT-E units are **not yet run** — the honest next step.

### Run status (Track C run once; remainder not yet run)

| | Count |
|---|---|
| PASS (raw verdict) | 5 |
| — of which grounded (asserting check, not exit-0) | 5 |
| — of which NOT grounded (blocked in this environment) | 0 |
| FAIL | 0 |
| not run (not yet executed — stated, never faked) | 68 |
| N/A (unsupported/retired — never run) | 0 |

### Release gate verdict (from the run verdicts so far; remainder pending)

| # | Gate | Source | Status | Evidence / honesty |
|---|---|---|---|---|
| 1 | CUJ-1..63 exercised end to end (63/63) | plan §8.1 | _pending_ | per-CUJ table below |
| 2 | Track A suites green (14/14) | §8.1 | _pending_ | suite logs + artifacts |
| 3 | Track B matrix: 19/19 agents × configured packs; skip = failure | §8.1 | _pending_ | `field-test/v0.1.0/results/track-b/` |
| 4 | Track C infra suites green on the field machine (5/5) | §8.1 | ✅ **PASS** | Track C 5/5 PASS, **5/5 grounded**; per-case: 4/6/1/10/8 passed, **0 skipped** |
| 5 | Required demonstrations recorded (4/4) | §8.1 / §4.4 | _pending_ | evidence refs |
| 6 | P0 enrichment suites green before the report (8/8) | §8.1 / §4.6 | _pending_ | suite results |
| 7 | 100% of planned scenarios pass after defect fixes (31.5) | §8.2 | _pending_ | 0 defects found so far; Track C green |
| 8 | First run ≤ 15 min on a clean machine, zero code changes (CUJ-24) | §8.2 | _pending_ | timed run log (FT-A-QUICKSTART not yet run) |
| 9 | Framework compatibility row: `field-smoke` green on 8/8 frameworks (or misses stated) | §8.2 | _pending_ | Track B not yet run |
| 10 | Determinism A/B: 100% deterministic-metric identity (FT-E05) | §8.3 | _pending_ | A/B artifacts |
| 11 | Judge credibility published with CIs; zero `judge_drift` (FT-E06) | §8.3 | ◑ batch evidence | FT-C-JUDGE ran the oMLX judge suite 10/0 with a captured pair; FT-E06 itself not yet run |
| 12 | Fail-closed rate 100% on planted faults (FT-E07) | §8.3 | _pending_ | fault log |
| 13 | Scoring-theater plants caught 100% (FT-E21) | §8.3 | _pending_ | meta-verification output |
| 14 | Publish-gate honesty: 100% of bad-number plants rejected (FT-E22) | §8.3 | _pending_ | gate output |
| 15 | Secret-leak sweep: 0 findings beyond the dummy key (FT-E08) | §8.3 | ◑ batch evidence | per-case `no-secret-leak` green + scan_results clean (36 files); FT-E08 itself not yet run |
| 16 | Evidence completeness 100% (FT-E20) | §8.3 | ◑ batch evidence | all 5 Track C cases carry verdict+assertions+logs (+ LLM pairs where applicable); FT-E20 itself not yet run |
| 17 | Nightly job scheduled + green (FT-E14/E27) | §8.5 | _pending_ | workflow added; no scheduled run yet |
| 18 | Report published with the not-tested list — 100% with reasons | §8.1/§8.6 | ◑ partial | this document states the 68 not-run units by name |

## Environment

| Item | Value |
|---|---|
| Host | macOS `Darwin` **arm64** (Apple Silicon) |
| Docker / Compose | Docker **29.5.2** (build 79eb04c7d8) · Compose **5.6.1** |
| Images | `agentdrill-fieldtest:local` (2.27 GB, the SUT) · `agentdrill-agent-runner:latest` (837 MB, sandbox) |
| oMLX endpoint | `http://127.0.0.1:8000/v1` (host) · `http://host.docker.internal:8000/v1` (containers) |
| oMLX model (agents) | `Qwen3.5-4B-4bit` |
| Judge model / provider | `Qwen3.5-9B-MLX-4bit` (same oMLX endpoint, OpenAI-compatible) |
| Tier(s) run | `local` (oMLX) — the only tier run so far |
| Agents under test | 19 agents pinned in `field/list.txt` (§4.5.1 closed) — **not yet run** (Track B pending) |
| RoE | not required for Track C (no Wave-0 firing); a signed RoE gates the Track A Wave-0 suites (pending) |
| Results | `field-test/v0.1.0/results/track-c/` — **committed** (harness `scripts/fieldtest/`; sanitized + gated) |

Source: `field-test/v0.1.0/results/track-c/env.json` (recorded per run).

## What Was Tested

**Track C — docker / LLM infrastructure (5/5 PASS, deep-verified).** The layer the whole run depends on. One suite
(`track-c`), on the `local` (oMLX) tier, macOS arm64:

- `FT-C-IMAGE` — the field image **builds** and the `agentdrill` CLI works in-container (`tests/test_docker.py -m docker`; 4 passed / 0 skipped).
- `FT-C-CONTAINER-LLM` — a **container reaches the host oMLX** via `host.docker.internal` and completes a real call (1/0).
- `FT-C-SANDBOX` — `run_in_container` sandbox paths (6/0).
- `FT-C-JUDGE` — the **LLM-as-judge** works against the pinned local model (10/0).
- `FT-C-ADAPTERS` — the adk/autogen/llamaindex/smolagents adapters **drive real agents** against the live endpoint (8/0).

**Deep verification (what each PASS actually proved).** Every assertion records the command it ran and a
**grounded** flag; the harness refuses a pass with no grounded assertion. Re-derived from disk
(`check_grounding.py`): **5/5 grounded, 0 over-claimed**, 2–4 grounded checks per case. Each `run_pytest.py`
invocation reported **0 skipped / 0 failed** — a skip here would have failed the case. Each LLM case captured a
**real 2xx** request/response pair (`model=Qwen3.5-4B-4bit`, `choices` present, sanitized). Leak gate:
`scan_results.py` clean over **36 files**.

**Not yet run (68 units — stated plainly, never faked):** Track A (14), the four required demonstrations, Track B
(19 agents), and the 31 FT-E enrichment units. The enrichment cadence is P0-gates-the-report / P1-nightly /
P2-scheduled (plan §4.6); none has run yet.

**Status vocabulary:** **PASS | FAIL | not run (declared) | N/A** — plus the journal qualifiers:
**✓ grounded** (an asserting check backs the verdict) · **HARDENED** (a weak assertion strengthened and re-run
green) · **FIXED** (a first-pass failure, fixed, re-run green) · **⛔ blocked** (needs tooling absent here — never
faked) · **DECLARED** (not run, with a named reason). A PASS that is not grounded is **⚠ over-claimed** and is
treated as not proven until hardened.

**Class vocabulary:** **P/F** = a hard pass/fail gate · **P/F\|D** = pass/fail-or-declare (a named declaration is
acceptable when the environment cannot provide — never a silent skip).

## Scenario Results (Master Table)

| Case | Suite | Class | Status | Notes |
|---|---|---|---|---|
| FT-A-ADD-DETONATE | track-a | P/F | not run | — |
| FT-A-ADD-GOV | track-a | P/F | not run | — |
| FT-A-ADD-LAB | track-a | P/F | not run | — |
| FT-A-ADD-NEUTRAL | track-a | P/F | not run | — |
| FT-A-ADD-PLATFORM | track-a | P/F | not run | — |
| FT-A-ADD-PROOF | track-a | P/F | not run | — |
| FT-A-CORE | track-a | P/F | not run | — |
| FT-A-KILLCHAIN | track-a | P/F | not run | — |
| FT-A-LIFECYCLE | track-a | P/F | not run | — |
| FT-A-QUICKSTART | track-a | P/F | not run | — |
| FT-A-SCALE | track-a | P/F | not run | — |
| FT-A-SELF | track-a | P/F | not run | — |
| FT-A-TRUST | track-a | P/F | not run | — |
| FT-A-VERIFY-OFFLINE | track-a | P/F\|D | not run | — |
| FT-B-ADK-OFFICIAL | track-b | P/F | not run | — |
| FT-B-ADK-QS | track-b | P/F | not run | — |
| FT-B-ADK-SOKART | track-b | P/F | not run | — |
| FT-B-AG-AZURE | track-b | P/F | not run | — |
| FT-B-AG-OFFICIAL | track-b | P/F | not run | — |
| FT-B-CREW-EXAMPLES | track-b | P/F | not run | — |
| FT-B-CREW-QS | track-b | P/F | not run | — |
| FT-B-CREW-QUICKSTARTS | track-b | P/F | not run | — |
| FT-B-LG-AZURE | track-b | P/F | not run | — |
| FT-B-LG-OFFICIAL | track-b | P/F | not run | — |
| FT-B-LI-AZURE | track-b | P/F | not run | — |
| FT-B-LI-OFFICIAL | track-b | P/F | not run | — |
| FT-B-OA-AZURE | track-b | P/F | not run | — |
| FT-B-OA-OFFICIAL | track-b | P/F | not run | — |
| FT-B-PAI-AZURE | track-b | P/F | not run | — |
| FT-B-PAI-OFFICIAL | track-b | P/F | not run | — |
| FT-B-SM-DEEPSEARCH | track-b | P/F | not run | — |
| FT-B-SM-QS | track-b | P/F | not run | — |
| FT-B-SM-SMOLCC | track-b | P/F | not run | — |
| FT-C-ADAPTERS | track-c | P/F | PASS | ✓ grounded (4): adk/autogen/llamaindex/smolagents adapters drive real agents against the live oMLX endpoint — **8 passed / 0 skipped**; real 2xx LLM pair captured + sanitized |
| FT-C-CONTAINER-LLM | track-c | P/F | PASS | ✓ grounded (4): container reaches host oMLX via host.docker.internal — **1 passed / 0 skipped**; real 2xx pair captured (model=Qwen3.5-4B-4bit, choices present) + sanitized |
| FT-C-IMAGE | track-c | P/F | PASS | ✓ grounded (2): field image builds; agentdrill CLI works in-container (`tests/test_docker.py -m docker`) — **4 passed / 0 skipped** |
| FT-C-JUDGE | track-c | P/F | PASS | ✓ grounded (4): LLM-as-judge against the pinned oMLX model (`Qwen3.5-9B-MLX-4bit`) — **10 passed / 0 skipped**; real 2xx pair captured + sanitized |
| FT-C-SANDBOX | track-c | P/F | PASS | ✓ grounded (2): `run_in_container` sandbox paths — **6 passed / 0 skipped** |
| FT-D-1-VERIFIER-OFFLINE | demos | P/F\|D | not run | — |
| FT-D-2-WITNESS-MISSED | demos | P/F | not run | — |
| FT-D-3-WITNESS-DISCREPANCY | demos | P/F | not run | — |
| FT-D-4-ROE-ABORT | demos | P/F | not run | — |
| FT-E01 | ft-e-p0 | P/F | not run | — |
| FT-E02 | ft-e-p0 | P/F | not run | — |
| FT-E03 | ft-e-p1 | P/F | not run | — |
| FT-E04 | ft-e-p1 | P/F | not run | — |
| FT-E05 | ft-e-p0 | P/F | not run | — |
| FT-E06 | ft-e-p0 | P/F | not run | — |
| FT-E07 | ft-e-p0 | P/F | not run | — |
| FT-E08 | ft-e-p0 | P/F | not run | — |
| FT-E09 | ft-e-p1 | P/F | not run | — |
| FT-E10 | ft-e-p1 | P/F | not run | — |
| FT-E11 | ft-e-p1 | P/F | not run | — |
| FT-E12 | ft-e-p1 | P/F | not run | — |
| FT-E13 | ft-e-p1 | P/F | not run | — |
| FT-E14 | ft-e-p1 | P/F | not run | — |
| FT-E15 | ft-e-p2 | P/F | not run | — |
| FT-E16 | ft-e-p2 | P/F | not run | — |
| FT-E17 | ft-e-p2 | P/F | not run | — |
| FT-E18 | ft-e-p2 | P/F | not run | — |
| FT-E19 | ft-e-p2 | P/F | not run | — |
| FT-E20 | ft-e-p2 | P/F | not run | — |
| FT-E21 | ft-e-p0 | P/F | not run | — |
| FT-E22 | ft-e-p0 | P/F | not run | — |
| FT-E23 | ft-e-p1 | P/F | not run | — |
| FT-E24 | ft-e-p1 | P/F | not run | — |
| FT-E25 | ft-e-p1 | P/F\|D | not run | — |
| FT-E26 | ft-e-p1 | P/F | not run | — |
| FT-E27 | ft-e-p1 | P/F | not run | — |
| FT-E28 | ft-e-p1 | P/F\|D | not run | — |
| FT-E29 | ft-e-p2 | P/F | not run | — |
| FT-E30 | ft-e-p2 | P/F | not run | — |
| FT-E31 | ft-e-p2 | P/F | not run | — |

**Totals:** 5 PASS · 0 FAIL · 68 not run · 0 N/A  (of 73 field units).

## Track B Matrix (per-agent rollup placeholders)

Filled per sweep by `scripts/fieldtest/run_agent.py` → `field-test/v0.1.0/results/track-b/` (committed): per-scenario verdicts → per-agent counts → pass rate
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

### track-a

14 case(s): 0 PASS · 0 FAIL · 14 not run · 0 N/A

### demos

4 case(s): 0 PASS · 0 FAIL · 4 not run · 0 N/A

### track-b

19 case(s): 0 PASS · 0 FAIL · 19 not run · 0 N/A

### track-c

5 case(s): 5 PASS · 0 FAIL · 0 not run · 0 N/A

### ft-e-p0

8 case(s): 0 PASS · 0 FAIL · 8 not run · 0 N/A

### ft-e-p1

14 case(s): 0 PASS · 0 FAIL · 14 not run · 0 N/A

### ft-e-p2

9 case(s): 0 PASS · 0 FAIL · 9 not run · 0 N/A

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

No failures recorded.

## Defect Catalogue

| Case | Suite | Failed assertions | Evidence |
|---|---|---|---|
| — | — | — | — |

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

#### Batch 1 — Track C (docker / LLM infrastructure), 2026-10-25

- **Run:** `bash scripts/fieldtest/run-ft-all.sh track-c` (log `/tmp/ft_small_batch.log`); results committed under
  `field-test/v0.1.0/results/track-c/`.
- **Verdicts:** **5 PASS · 0 FAIL · 0 declared**.
- **Deep verification:** `check_grounding.py` → 5/5 grounded, 0 over-claimed; `scan_results.py` → clean (36 files).

| Case | Verdict | What the step actually asserted | Gap vs the plan condition | Call |
|---|---|---|---|---|
| FT-C-IMAGE | PASS | `run_pytest.py tests/test_docker.py -m docker` → **4 passed / 0 skipped** (image builds; `--help`/`version`/`validate`/`run` in-container) | none — the plan's "image builds; CLI works in-container" | ✓ grounded |
| FT-C-SANDBOX | PASS | `run_pytest.py tests/test_security_container_integration.py -m docker` → **6 passed / 0 skipped** (`run_in_container` env-allowlist/exec paths) | none | ✓ grounded |
| FT-C-CONTAINER-LLM | PASS | `run_pytest.py tests/test_security_docker_llm.py -m docker` → **1 passed / 0 skipped** (container→host oMLX) **+** `ft_llm_probe` captured a **real 2xx** pair | probe uses the agent model (4B); the container→LLM test itself proves the path — no gap in the claim | ✓ grounded |
| FT-C-JUDGE | PASS | `run_pytest.py tests/test_judge_omlx_integration.py -m omlx` → **10 passed / 0 skipped** (real `JudgeVerdict`s from the pinned oMLX model) **+** 2xx pair captured | none | ✓ grounded |
| FT-C-ADAPTERS | PASS | `run_pytest.py tests/test_adapters_{adk,autogen,llamaindex,smolagents}_llm.py -m omlx` → **8 passed / 0 skipped** (each adapter drives a real agent) **+** 2xx pair captured | none | ✓ grounded |

**Per-case evidence notes.**

- **No skips anywhere.** `run_pytest.py` fails on any skipped test; every suite reported `0 skipped`. A skipped
  `-m docker`/`-m omlx` test would have failed the case rather than passing silently.
- **LLM captures are real.** All three LLM cases' `artifacts/llm/*-response.json` are `status_code: 200` with a
  non-empty body containing `choices`, model `Qwen3.5-4B-4bit`; the pairs are sanitized (no unmasked key).
- **Judge model.** `FT-C-JUDGE` exercises `Qwen3.5-9B-MLX-4bit` inside the oMLX judge suite (the probe pair uses
  the agent model, 4B — noted above, not a gap).

**Harness noise (benign):** none observed in this batch (the earlier `/commands.log: Read-only file system`
warning was fixed by guarding `ft_record` when no case dir is active).

#### Batch 2+ — pending (Track A · demos · Track B · FT-E)

_not yet run._ These 68 units run next; each will be deep-verified the same way before this report is re-filled.

### Hardening backlog — every PASS

Status: **G** grounded · **R** run-only · **V** vacuous. Every PASS must be grounded or explicitly blocked.

| Suite | Case | Now (G/R/V) | Hardening needed |
|---|---|---|---|
| track-c | FT-C-IMAGE, FT-C-SANDBOX, FT-C-CONTAINER-LLM, FT-C-JUDGE, FT-C-ADAPTERS | **G** | — (all grounded; 0 skipped) |

### Hardening progress log

| Case | New assertion | Result |
|---|---|---|
| — | — | — |

## Issues Found & Fixed During Validation

> Numbered (F-1, F-2, …), newest last; classify each as **harness** or **product** — keep the classes honest
> (plan §7).

**No product defects found.** The Track C batch was green first-run; the issues below are **harness/setup**
issues found while bringing the harness up (not product defects), each fixed and re-verified — see the git
history of `scripts/fieldtest/`.

| # | Class | Issue | Fix | Re-verified |
|---|---|---|---|---|
| V-1 | harness | `docker compose -f scripts/fieldtest/...` resolved the build context against the overlay dir (`context: .` → `scripts/fieldtest`) | added `--project-directory "$REPO_ROOT"` to `STACK_COMPOSE` | `stack-ft.sh up` builds + READY |
| V-2 | harness | LLM probe fell through to the **ambient `OPENAI_BASE_URL`/`OPENAI_MODEL`** (a coding-agent endpoint) → HTTP 403/404 | namespaced all vars `FT_LLM_*`; `llm_capture.py` only reads `FT_LLM_*` (+ explicit flags); never sends ambient keys | FT-E06/FT-C-JUDGE/FT-C-ADAPTERS capture real 2xx from oMLX |
| V-3 | harness | LLM capture "passed" on an **error stub** (response file existed but `status_code: 0`) | `ft_assert_llm_capture` now requires a **real 2xx with a non-empty body** | FT-E06 (and Track C) |
| V-4 | harness | `-m omlx` matched nothing on unit-test files → pytest exit 5 | FT-E06/FT-E29 run without a marker; `run_pytest.py` fails loudly on "no tests ran" | FT-E06 green |
| V-5 | harness | benign `/commands.log: Read-only file system` write before any case dir exists | `ft_record` no-ops when no case dir is active | batch log clean |
| V-6 | **product-adjacent** | `build_report.py` used an f-string backslash escape → **SyntaxError on Python 3.11** (the repo's floor) | hoisted the escape out of the f-string | `ruff` + `bash`/py parse; report filled |

Class vocabulary: **harness** = field-test wiring · **product** = shipped code. V-6 is a real bug in the new
report tooling (would have crashed the report fill on 3.11); it is fixed. **Zero shipped-product defects.**

## Observations — themes fixed, what worked, what didn't

### Themes of issues fixed

1. **Environment bleed (systemic).** The surrounding shell exported `OPENAI_*/LLM_*`; the harness must be immune
   to it. Fixed by namespacing every field-test LLM var `FT_LLM_*` and never reading ambient `OPENAI_*`. This is
   the harness analogue of agentwatch's "a driver that reads the store must be shown to read a non-empty field".
2. **Compose path resolution.** An overlay in a subdirectory resolves relative paths against that directory;
   `--project-directory` pins them to the repo root.
3. **Weak "capture" checks.** An error stub must not count as a captured LLM pair — the check now demands a real
   2xx with a body.
4. **A real 3.11 syntax bug** in the new report tooling, caught by running the tool (not by reading it).

### What worked

- **Deep verification caught nothing to hide** — all 5 Track C passes are grounded (2–4 checks each) and every
  suite reported **0 skipped**; the gate (`check_grounding.py`) confirms it from disk.
- **LLM capture as the evidence** — the three LLM cases each show a real 2xx pair from oMLX, sanitized.
- **The readiness gate** — `stack-ft.sh up` waited for `running+healthy` then the SUT answering then oMLX, and
  wrote the transcript to a preserved log rather than declaring "up" on a started container.
- **No skips by construction** — `run_pytest.py` turns a skipped docker/omlx test into a failure.

### What didn't work (and what we did about it)

- **Ambient env leaked into the LLM probe** (V-2) — the probe hit a coding-agent endpoint (403/404). Fixed by
  namespacing to `FT_LLM_*`; re-run green against oMLX.
- **A capture "pass" on an error stub** (V-3) — tightened to require a real 2xx body.
- **`-m omlx` on unit tests** (V-4) — pytest exit 5 ("no tests collected"); fixed the case wiring and made
  `run_pytest.py` fail on "no tests ran".
- **A 3.11 f-string SyntaxError** in `build_report.py` (V-6) — would have crashed the report fill; fixed.

### Harness vs product

Every issue this batch surfaced was **harness/setup wiring** (V-1…V-5) plus one bug in the new **report tooling**
(V-6) — **zero shipped-product defects**. The Track C product behaviour (image/CLI, container→LLM, sandbox,
judge, adapters) was correct first-run, and the harness assertions are the reason that can be stated plainly.

## Learnings

1. **A PASS is only real when the assertion is real.** `check_grounding.py` re-derives grounding from the
   recorded command — an import/existence/`||true` shape can never justify a pass.
2. **A skip is a failure.** `run_pytest.py` fails on any skipped docker/omlx test, so a "green" cannot hide a
   test that never ran.
3. **Capture the pair, and demand a real one.** An error stub (`status_code: 0`) must not satisfy the LLM-capture
   must; require 2xx + a body.
4. **Env bleed is silent.** The harness must own its LLM variables (`FT_LLM_*`) — never trust the surrounding
   shell's `OPENAI_*`.
5. **Readiness ≠ "container started".** Wait for healthy + the SUT answering (+ the LLM) before saying "up".
6. **Run the tool, don't read it.** The 3.11 f-string SyntaxError in `build_report.py` was invisible on read and
   fatal on Python 3.11 — the repo's floor.
7. **Persist the evidence.** Verdicts, assertions, logs and LLM pairs are committed; the report is derived from
   them, never hand-edited.

## Takeaways

- The **Track C docker/LLM infrastructure layer is verified green and deeply grounded** — the layer the rest of
  the run depends on. That is the meaningful result of this batch.
- The harness enforces its own honesty: grounding, no-skip, real LLM captures, leak gate, readiness wait.
- The remaining 68 units (Track A, demos, Track B, FT-E) run next, with the same deep verification.

## Deferred Items (pre-run preconditions — plan §4.5)

Each precondition must close before its suite runs, or the suite **declares** (never silently skips). Track
disposition here.

| # | Item (plan §4.5) | Blocks | Disposition |
|---|---|---|---|
| 1 | Pin the 19 agent SHAs (`field/list.txt` all `TODO`) | Track B determinism; FT-E11 | ✅ **closed** — all 19 pinned in `field/list.txt` |
| 2 | `field/setup.sh` default list points at nonexistent `field/list1.txt` | Track B setup | ✅ **closed** — `setup.sh` now defaults to `field/list.txt` |
| 3 | Runtime image bakes only `scenarios/` — `packs/` + `field/` not in image | in-container demo/quickstart (§5.6/5.7) | ✅ **closed** — image bakes `packs/`+`scenarios/` and the compose binds them at `/ft/packs` `/ft/scenarios` |
| 4 | Image extras partial (`[dev,judge,langgraph,pydanticai]`) | in-container matrix variants | ✅ **closed** — the field image installs all 8 framework extras |
| 5 | macOS-built agent venvs cannot run in Linux containers | FT-E25; §5.7 variant | ⚠ **open** — Track B/D runs host-side; FT-E25 declares |
| 6 | Dockerfile label/license mismatch (MIT vs Apache-2.0) | release scans (M32) | ⚠ **open** — repo `Dockerfile` label; M32 release scan |
| 7 | Nightly CI runner choice (no MLX on hosted runners) | FT-E14; §5.9 | ✅ **closed** — `.github/workflows/fieldtest.yml` targets a self-hosted macOS+arm64 runner |
| 8 | `agentdrill verify` CLI is a planned stub | FT-A-VERIFY-OFFLINE; FT-D-1; FT-E12 | ⚠ **open** — its cases resolve `declared` (honest, not faked) |
| 9 | `agentdrill run --dry-run`/`--explain` documented but unwired | FT-E28 | ⚠ **open** — FT-E28 resolves `declared` |
| 10 | Optional minimal `docker compose` (agentdrill + Ollama sidecar) | one-command env | ✅ **superseded** — oMLX is host-only; the overlay is the minimal stack (no sidecar) |

## Coverage, Gaps, and Declared Limitations

Status vocabulary: **not run | PASS | FAIL | N/A** — this run so far: **5 PASS · 0 FAIL · 68 not run**.

- **Coverage:** **5 of 73** field units run (Track C), **5/5 PASS grounded** (0 over-claimed, 0 skipped).
- **Gaps:** no hardenable cases; **68 units not yet run** — Track A (14), demos (4), Track B (19), FT-E (31).
- **Not tested (honest — mandatory, with reasons):**
  - **Track A / demos / Track B / FT-E — 68 units not yet run** (this was a Track C batch). Track A Wave-0
    suites additionally need a signed RoE + the deployed enforcer stack (absent here → `declared`).
  - **Track B** needs the 19 agent clones' per-agent venvs + the sweep (host-side).
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
| Track C infra suites green | 5/5 | ✅ **5/5** | `field-test/v0.1.0/results/track-c/summary.json` (0 skipped) |
| Required demonstrations recorded | 4/4 | _pending_ | §4.4 evidence refs |
| Enrichment suites | P0 8/8 before the report; P1 nightly; P2 scheduled | _pending_ | §4.6 results |
| Agent SHA pinning | 100% | ✅ **100%** | `field/list.txt` (19 pinned) |
| Not-tested list completeness | 100% with reasons | ◑ **68 named** | this report §Coverage |

### 8.2 Outcomes

| Measure | Target | Achieved | Evidence |
|---|---|---|---|
| Scenario pass rate (milestone bar) | 100% after defect fixes | _pending_ | `run.json`/`summary.json` |
| Per-agent acceptance (triage bar) | ≥ `minimum_pass_rate` (0.5) each | _pending_ | per-agent rollup |
| Skip/quarantine discipline | every skip = failure with reason | ✅ **Track C: 0 skipped** | per-suite `ok: N passed, 0 skipped` |
| Exit codes | 0 green; non-zero classified (§5.8) | _pending_ | suite exit codes |
| Defect closure | 100% fixed with a linked regression test | _pending_ | defects table |
| Framework compatibility row | `field-smoke` green 8/8 (or misses stated) | _pending_ | compatibility table |
| First-run (CUJ-24) | ≤ 15 min, zero code changes | _pending_ | timed run log |

### 8.3 Trust

| Measure | Target | Achieved | Evidence |
|---|---|---|---|
| Determinism A/B (FT-E05) | 100% deterministic-metric identity | _pending_ | A/B artifacts |
| Judge credibility (FT-E06) | rates with CIs; zero `judge_drift` | _pending_ | calibration output |
| Judge non-mock guard | 100% provider ≠ `mock` + evidence files | ◑ **Track C** | FT-C-JUDGE 10/0 against real oMLX (not mock) |
| Fail-closed rate (FT-E07) | 100%, right exit codes, zero silent greens | _pending_ | fault log |
| Theater plants caught (FT-E21) | 100% | _pending_ | meta-verification output |
| Publish-gate honesty (FT-E22) | 100% of bad-number plants rejected | _pending_ | gate output |
| Secret-leak sweep (FT-E08) | 0 findings beyond dummy `omlx-test` | ◑ **batch clean** | `scan_results.py` clean (36 files); every case `no-secret-leak` PASS |
| Evidence completeness (FT-E20) | 100% carry the full chain | ◑ **Track C** | all 5 cases: verdict+assertions+logs (+ LLM pairs) |

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
| Local-tier cost | $0.00; cloud within `--max-cost` | ✅ **$0.00** | local oMLX; no cloud calls |
| Cost-governor (FT-E15) | over-budget ⇒ loud `cost_exceeded` | _pending_ | governor log |
| Suite duration | within per-tier ceilings (5/10/15 min) | _pending_ | run timings |
| Cache savings | reported per sweep, provenance labeled | _pending_ | `cache_stats` |
| Nightly job (FT-E14/E27) | scheduled + green; release-shape gates green | _pending_ | CI history |

## Claims Ledger + Known-Limitations Shrink Evidence

> Gate: FT-E27 (claims linter zero violations; every published number has a ledger entry).
> [known-limitations.md](../../reference/known-limitations.md) is updated in the same pass (31.D, issue #91).

FT-E27 (claims linter + ledger) **not yet run** — this batch (Track C infra) produced no published claims, so
there is no ledger change. [known-limitations.md](../../reference/known-limitations.md) update is part of 31.D
and is not yet done.

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
| First-run (quickstart, CUJ-24) | ≤ 15 min | _pending_ (FT-A-QUICKSTART not yet run) |
| Per-scenario duration (local tier) | ≤ 30 s | _pending_ |
| Suite duration per tier | local 5 min · cheap 10 min · better 15 min | ◑ Track C batch: 5 cases (docker + oMLX pytest), complete |
| Track C per-suite pytest | 0 skipped / 0 failed | ✅ IMAGE 4 · SANDBOX 6 · CONTAINER-LLM 1 · JUDGE 10 · ADAPTERS 8 |
| Kill-time per stage (FT-A-KILLCHAIN) | p50/p95/max, ≥5 trials | _pending_ |
| Timeout-enforcement latency (FT-E16) | p50/p95, ≥5 trials | _pending_ |
| Judge cache savings | reported, provenance labeled | _pending_ |

## Results & Coverage Comparison

First field report for agentdrill — no prior version; this run is the **baseline** for future releases.

| | Plan (v0.1.0) | This run |
|---|---|---|
| Field units | 73 (A 14 · D 4 · B 19 · C 5 · E 31) | **5 run (Track C)** · 68 not run |
| CUJs exercised | 63/63 | **0/63** (CUJs run with Track A — not yet) |
| P0 enrichment green | 8/8 | **0/8** (FT-E not yet run) |

## Action Items

Done this pass (setup + verification + Batch 1):

1. [x] Closed §4.5 preconditions #1, #2, #3, #4, #7, #10 (see Deferred Items table); #5, #6, #8, #9 remain open and their cases declare.
2. [x] Preflight green: `docker info` + oMLX `/v1/models` (serves 4B agent + 9B judge) + version.
3. [x] Images built: `agentdrill-fieldtest:local` (SUT) + `agentdrill-agent-runner` (sandbox).
4. [x] **Track C run + deep-verified**: 5/5 PASS, grounded, 0 skipped, LLM pairs captured.
5. [x] Report filled from the committed verdicts (`build_report.py`) + this batch's deep analysis.

Next (in order):

6. [ ] Run Track A (14) + demos (4) + FT-E P0 (8) — `bash scripts/fieldtest/run-suite.sh track-a`, `… demos`, `… ft-e-p0`.
7. [ ] Run FT-E P1 (14) then P2 (9).
8. [ ] Run Track B (19): clones + host venvs; `run_agent.py` parses each sweep.
9. [ ] Close out `declared` cases that can be unblocked (`verify` CLI #8, `--dry-run` #9).
10. [ ] Re-run `check_grounding.py` + `scan_results.py` + `build_report.py`; commit the results.

## Reproducibility / Evidence Paths

**All runs are persisted in git** under `field-test/v0.1.0/results/<suite>/`: per
case `verdict.json` (status, class, grounded, assertions_total/grounded,
llm_captured), `assertions.ndjson` (each with the command it ran + a grounded
flag), `commands.log`, `stdout.log`/`stderr.log`, and `artifacts/` — including
`artifacts/llm/<name>-request.json` / `-response.json` (**retrieved LLM
request/response pairs**) and, for Track B, `artifacts/matrix/…`. Track B's live
runner output is copied in by `run_agent.py`; everything is sanitized and gated
(`scan_results.py`) so no unmasked secret is ever committed.

This batch: `field-test/v0.1.0/results/track-c/` (5 cases, `env.json`, `summary.{json,md}`).

Reproduce (the harness in `scripts/fieldtest/`):

```sh
# Environment + harness
cp scripts/fieldtest/.env.example scripts/fieldtest/.env
python3 scripts/fieldtest/gen_cases.py            # regenerate specs + steps
bash scripts/fieldtest/stack-ft.sh up              # agentdrill SUT (oMLX is host-side)

# Suites (results -> field-test/v0.1.0/results/<suite>/)
bash scripts/fieldtest/run-ft-all.sh               # all suites
bash scripts/fieldtest/run-suite.sh track-c        # one suite
bash scripts/fieldtest/run-case.sh FT-C-IMAGE      # one case

# Gates + report (all runs committed)
python3 scripts/fieldtest/check_grounding.py       # deep verification: every PASS grounded
python3 scripts/fieldtest/scan_results.py          # leak gate: no unmasked secrets
python3 scripts/fieldtest/build_report.py          # fill this report from the results
```

Exit codes (docs/reference/errors.md): `0` pass · `1` misses · `2` config · `3` judge/oracle infra ·
`4` critical miss · `5` critical divergence.

## Appendices

- Plan: [field-test-plan.md](field-test-plan.md) (suites §4, runbook §5, success measures §8, exit gate §9).
- Field workspace: [`field/README.md`](../../field/README.md) (runner controls, results layout).
- CI strategy: [docs/ci-field-tests.md](../../ci-field-tests.md) (tiers, ceilings, flake budget).
- Error contract: [docs/reference/errors.md](../../reference/errors.md).
- Issue tracker: [milestone 24](https://github.com/agentic-suite/agentsec-agentdrill/milestone/24) (#82–#91, #383).
