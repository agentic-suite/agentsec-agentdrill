# Field Test Plan (v0.1.0)

**Status:** plan of record for **M31 Field tests**
([milestone 24](https://github.com/agentic-suite/agentsec-agentdrill/milestone/24); WBS
[part 17](../wbs/v0.1.0/wbs-v0.1.0-part17-fieldtest-release.md) items 31.1–31.6 → issues
[#82](https://github.com/agentic-suite/agentsec-agentdrill/issues/82)–[#91](https://github.com/agentic-suite/agentsec-agentdrill/issues/91),
[#383](https://github.com/agentic-suite/agentsec-agentdrill/issues/383)).
The executed result of this plan is [FIELD_TEST_REPORT.md](FIELD_TEST_REPORT.md).

---

## BLUF — the three answers

1. **Docker setup.** Three layers: (1) the `agentdrill` image built from the repo [`Dockerfile`](../../Dockerfile)
   (two-stage, non-root, `agentdrill` CLI as entrypoint); (2) the `agentdrill-agent-runner` sandbox image used by
   `run_in_container` ([`security/sandbox.py`](../../src/agentdrill/security/sandbox.py)); (3) the per-agent virtualenvs
   under `field/agents/` (each cloned third-party agent gets its own env). The runner
   ([`field/run-local.sh`](../../field/run-local.sh)) drives everything serially with resume/pagination.
2. **Do we need an LLM?** **Yes, in exactly two roles — and nowhere else.** (a) the **agent under test** must call a
   real model whenever a real agent runs (the whole point of a *field* trial — mock models make it a unit test);
   (b) the **judge** (LLM-as-judge) is required for rubric-scored metrics and is *hard-asserted non-mock* in field
   runs. Docker image/CLI validation, deterministic oracles (exact / tool-trace / schema / tool-count), the offline
   verifier and the bundled demo stack need **no** LLM.
3. **Can we use a local LLM?** **Yes — local is the default tier.** The harness is already wired for it: an
   OpenAI-compatible **oMLX** server on the host (`http://127.0.0.1:8000/v1`, pinned Qwen models), plus **Ollama**
   and **MLXJudgeClient** backends. Cloud tiers (`cheap`/`better` via OpenRouter) are an *optional cross-check*
   for judge reliability, not a requirement. One hard constraint: **MLX cannot run inside a Linux container**, so
   oMLX stays on the host and containers reach it via `host.docker.internal:8000` (or use an Ollama sidecar).

---

## 1. Goal & scope

Run every critical user journey end to end against a **real deployed stack** (the Wave-0 enforcers) plus the
bundled demo, and publish an honest report — including what was **not** tested.

Two tracks, one report:

- **Track A — CUJ field suites.** Every CUJ-1..CUJ-63 exercised end to end (issues #83, #383) on the bundled demo
  stack and the real stack, under a signed RoE in an ephemeral/purple environment.
- **Track B — agent-harness field trials** (the [`field/`](../../field/README.md) workspace). The evaluation-harness
  surface driven against **19 real third-party agents across 8 frameworks** (LangGraph, PydanticAI, CrewAI, OpenAI
  Agents, smolagents, AutoGen/AG2, LlamaIndex, Google ADK), cloned at pinned SHAs, driven with scenario packs and
  scored by the real judge. This is where LLMs are exercised.
- **Track C — docker/LLM infrastructure suites** that gate the field environment itself (§4.3).

### CUJ coverage map (CUJ-1..63)

| Group | Cases |
|---|---|
| Core | run a pack (CUJ-1), gate a policy PR (CUJ-2), reproduce the benchmark (CUJ-3), drill an incident (CUJ-4) |
| Kill chain | verify kill-time (CUJ-5, CUJ-16) |
| Self-attack | evasion pack (CUJ-6), drill-the-drill (CUJ-25), oracle-vs-corpus (CUJ-26), scheduled drill (CUJ-27), dark holdout |
| Lifecycle | contribute/import a pack (CUJ-7), miss→fix loop (CUJ-8), intake→pack (CUJ-20), fix holds (CUJ-21), seams (CUJ-22), verify offline (CUJ-23), quickstart (CUJ-24) |
| Trust | efficacy (CUJ-19), attribution (CUJ-14), dispute (CUJ-13), HITL gray area (CUJ-17), defense contract (CUJ-15) |
| Scale | fleet rollup (CUJ-18), trigger re-drill (CUJ-12), trend (CUJ-9), coverage (CUJ-10) |
| **Additions — strength & proof** | `Hold@k` gate (CUJ-28), read an honest number (CUJ-29), the log lied / witness discrepancy (CUJ-30), proof without telemetry (CUJ-31) |
| **Additions — lab & bypass** | author a rug-pull case (CUJ-32), carrier matrix (CUJ-33), bypass + minimal repro (CUJ-34), coverage not just green (CUJ-35) |
| **Additions — neutrality & integration** | pick between defenses (CUJ-36), reproduce the OSS table (CUJ-37), inline in the PR (CUJ-54), did the SOC see it (CUJ-55) |
| **Additions — context & governance** | don't ship the outage (CUJ-38), shadow then promote (CUJ-39), trifecta inventory (CUJ-40), new path fails the gate (CUJ-41), hours not days (CUJ-42), cite or drop (CUJ-43), sanctioned exception (CUJ-44), visible miss, it expired (CUJ-45), admission gate on freshness (CUJ-46), underwriter verification (CUJ-47), authorized to fire (CUJ-48), abort in seconds (CUJ-49) |
| **Additions — detonation & frontier** | before allowlisting (CUJ-50), registry admission (CUJ-51), submit and get credit (CUJ-52), convert to a regression (CUJ-53), approval dialog truth (CUJ-56), contain the cascade (CUJ-57) |
| **Additions — explorer, platform & standards** | red CI to root cause (CUJ-58), adjudicate at speed (CUJ-59), per-harness depth (CUJ-60), add my harness (CUJ-61), auditor evidence index (CUJ-62), contributor tag lint (CUJ-63) |

Full CUJ definitions: [PRD 04](../prd/04-users-and-cujs.md). Success criteria: [PRD 07](../prd/07-success-metrics.md).

---

## 2. Environment — the docker setup

### 2.1 Topology

| Layer | What | Runs where |
|---|---|---|
| **Host** (Apple Silicon macOS) | Docker Desktop daemon, **oMLX server** (`127.0.0.1:8000/v1`, OpenAI-compatible, MLX-backed), agent source clones + per-agent `.venv`s | host |
| **`agentdrill` image** | Built from repo root [`Dockerfile`](../../Dockerfile): two-stage (wheel builder → slim runtime), Python 3.11, `agentdrill` wheel + `[dev,judge,langgraph,pydanticai]` extras, non-root user, `scenarios/` baked in, `docker-ce-cli` included so it can launch sibling containers | container |
| **`agentdrill-agent-runner` image** | Sandbox image used by `run_in_container` (`DockerConfig`) for sandboxed agent execution (`--sandbox`); env allowlist, 2× timeout | container |
| **LLM endpoint** | oMLX on the host — reached from containers via `http://host.docker.internal:8000/v1` (Docker Desktop on macOS; `add_host_gateway: true` on Linux). Fully-containerized fallback: an **Ollama** sidecar | host (default) or sidecar |

### 2.2 Networking facts (verified against the code)

- `tests/test_security_docker_llm.py` already uses `http://host.docker.internal:8000/v1/chat/completions` for
  container→host LLM calls — the field runs reuse exactly this pattern.
- MLX requires Apple Silicon **Metal** → the local LLM server **cannot** be moved into a Linux container. Either
  keep oMLX on the host (default) or swap in Ollama/llama.cpp as a container sidecar.
- The runtime image includes `docker-ce-cli` — mounting `/var/run/docker.sock` lets the harness launch sibling
  sandbox containers. **Only in the ephemeral/purple field environment**, never in normal use.

### 2.3 Images the field run needs

| Image | Built by | Purpose |
|---|---|---|
| `agentdrill-test` | `tests/test_docker.py` (module fixture) | in-container CLI validation (help/version/validate/run) |
| `agentdrill-agent-runner` | pre-built (`docker build -t agentdrill-agent-runner -f Dockerfile .`), overridable via `AGENTDRILL_DOCKER_IMAGE` | `run_in_container` sandbox + `tests/test_security_docker_llm.py` |
| `agentdrill:field` (any tag) | same Dockerfile | ad-hoc in-container CLI/demo runs |

---

## 3. Do the tests need an LLM?

Two distinct roles — decide each separately:

| Role | Needed for | Not needed for |
|---|---|---|
| **Agent-under-test model** | any run that drives a **real agent** (all of Track B; Track A on the real stack, where the deployed harness brings its own model) | the bundled demo stack (offline, synthetic, `mock`-attested), docker image/CLI validation, offline verifier runs |
| **Judge model** (LLM-as-judge) | rubric-scored metrics (`task_completion`, `output_correctness`, refusal/gray-area criteria) — the field test **hard-asserts** judge provider ≠ `mock`, requires LLM HTTP capture + judge prompt/verdict evidence on disk for every judge metric ([`field/test_field_agent.py`](../../field/test_field_agent.py) §5a) | deterministic metrics: `exact`, `tool_trace`, `schema`, `tool_called`, `zero_disallowed_actions`, `step_efficiency` |

So: **yes for the field matrix and judge-scored CUJs; no for image validation, deterministic oracles, the demo
stack and the offline verifier.** A "field test" that replaces the agent's model with a mock is a unit test and
must not be reported as field coverage.

### 3.1 Can we use a local LLM? — yes, and it is the default

| Option | How | Notes |
|---|---|---|
| **oMLX (default, `--tier local`)** | host server at `http://127.0.0.1:8000/v1`; pinned models `Qwen3.5-4B-4bit` (agents) and `Qwen3.5-9B-MLX-4bit` (judge/worker default) | $0, offline, fastest on Apple Silicon; the runner exports `AGENTDRILL_FIELD_ENDPOINT`/`AGENTDRILL_FIELD_MODEL`, `AGENTDRILL_FORCE_MODEL=1`, dummy key `omlx-test` |
| **Ollama** | `AGENTDRILL_FIELD_JUDGE_PROVIDER=ollama` (defaults `http://localhost:11434`) | fully containerizable → the right choice for hosted-CI nights |
| **MLXJudgeClient** | `AGENTDRILL_FIELD_JUDGE_PROVIDER=mlx` (manages an `mlx-lm` server) | judge-only |
| **Cloud cross-check (optional)** | `--tier cheap` (`openai/gpt-4o-mini`) or `--tier better` (`openai/gpt-4o`) via `https://openrouter.ai/api/v1` + `OPENROUTER_API_KEY` | used to cross-validate judge verdicts for the *published* report; never required for a green field run |

Honesty constraints on the local LLM (state them in the report, per [PRD 23](../prd/23-oracle-credibility.md)):

- **Judge quality is model-bound.** A 4–9B local judge is weaker than a frontier judge; rubric metrics inherit
  that variance. Mitigations already in the harness: `temperature=0`, pinned model ids, per-metric judge
  prompt + verdict + rationale evidence, and the provider≠`mock` guard. The published rows must carry the judge
  model label.
- **Determinism:** deterministic-metric rows are model-independent; LLM-bound rows are evidence-bound (recorded
  trajectories + verdicts), not bit-reproducible — this is acceptable for field *pass/fail*; multi-seed means±std
  remain the benchmark's (M32) concern, not the field gate's.
- **Contamination:** pinned open-weights models (Qwen) on our own synthetic scenarios → no training-data overlap
  concern; cloud-judge rows are flagged if any case text is plausibly in the judge model's training data
  ([PRD 20](../prd/20-efficacy-freshness-lifecycle.md)).

---

## 4. What field tests need to be written

### 4.1 Track A — CUJ end-to-end suites (issues #83, #383)

Each suite: fresh environment → execute → capture evidence → classify failures (shim / wrong config / adapter /
oracle) → fix with a regression test (31.5) → record in [FIELD_TEST_REPORT.md](FIELD_TEST_REPORT.md) per CUJ.

| Suite | CUJs | What runs | Stack | LLM? |
|---|---|---|---|---|
| FT-A-QUICKSTART | 24 | timed first run ≤ 15 min on a clean machine/env (`agentdrill quickstart`; docker-pull variant) | demo | no |
| FT-A-CORE | 1, 2, 3, 4 | run a pack, gate a policy PR (a rule that un-blocks an attack is rejected), reproduce a published benchmark, drill a named incident | demo + Wave-0 | real-stack agent model; judge for gray areas |
| FT-A-KILLCHAIN | 5, 16 | kill-time to probed cessation; full kill-chain timeline (p50/p95/max) | Wave-0 | real |
| FT-A-SELF | 6, 25, 26, 27 | evasion pack on ourselves, drill-the-drill, instrument check, oracle-vs-corpus, scheduled drill, dark holdout | demo + Wave-0 | judge (labeled) |
| FT-A-LIFECYCLE | 7, 8, 20, 21, 22 | import a pack, miss→policy-fix loop, intake→pack (7-day freshness), fix holds, seam probing | demo | partial |
| FT-A-TRUST | 11, 13, 14, 15, 17, 19 | auditor single-finding offline verify, dispute SLA, attribution, defense contract, HITL gray-area review, efficacy control (unguarded success) | demo + Wave-0 | judge (labeled) |
| FT-A-SCALE | 9, 10, 12, 18 | trend, coverage heat-map, trigger re-drill, fleet rollup | demo | no |
| FT-A-VERIFY-OFFLINE | 23 (+11) | standalone verifier on a machine that never ran the drill; bundle verified via docker `--read-only`. **Note:** the `agentdrill verify` CLI surface is currently a *planned stub* (engine exists in `lifecycle/verifier.py`) — wiring it is a 31.1 precondition (§4.5) | none | no |
| FT-A-ADD-PROOF | 28–31 | `Hold@k` pressure gate, honest-number readout, **witness-confirmed `missed`** and **`witness_discrepancy`** (both *required demonstrations*, WBS part 17), proof without telemetry | Wave-0 | judge (labeled) |
| FT-A-ADD-LAB | 32–35 | rug-pull case authoring, carrier matrix, bypass + minimal repro, coverage-not-just-green | lab | judge (labeled) |
| FT-A-ADD-NEUTRAL | 36, 37, 54, 55 | BYOD head-to-head, OSS-table reproduction, inline-in-PR, SOC visibility | BYOD stack | judge (labeled) |
| FT-A-ADD-GOV | 38–49 | backtest/shadow, trifecta inventory, new-path-fails-gate, hours-not-days, cite-or-drop, sanctioned-exception waiver, visible miss, expired-waiver auto-reopen, freshness admission gate, underwriter verification, authorized-to-fire, **RoE abort in seconds** (*required demonstration*) | Wave-0 | — |
| FT-A-ADD-DETONATE | 50–53, 56, 57 | pre-allowlist detonation, registry admission, submit-and-get-credit, convert-to-regression, approval-dialog truth, cascade containment | detonation lab | — |
| FT-A-ADD-PLATFORM | 58–63 | explorer root-cause, fast adjudication, per-harness depth, add-my-harness, auditor evidence index, contributor tag lint | demo | — |

RoE: any suite that fires attack packs against Wave-0 runs **only** under a signed RoE with the fail-closed
preflight and safe-fire interlocks ([RoE reference](../reference/exposure-attestation-roe.md),
[ADR 0012](../adr/0012-rules-of-engagement.md)); `RoEError`/out-of-scope cases must refuse to fire — that refusal
is itself asserted.

### 4.2 Track B — agent-harness field matrix (the `field/` workspace)

Real third-party agents ([`field/list.txt`](../../field/list.txt)) × scenario packs
([`field/scenarios/`](../../field/scenarios/)) × LLM tier. The runner:
clone at pinned SHA → per-agent setup (`field/config/<slug>.json` `setup_commands`) → run each scenario via the
pytest plugin (`field/test_field_agent.py`) → score with the real judge → assert pass → persist evidence.

- **Agents (19):** `lg-azure` `lg-official` · `pai-azure` `pai-official` · `crew-quickstarts` `crew-examples`
  `crew-qs` · `oa-azure` `oa-official` · `sm-qs` `sm-smolcc` `sm-deepsearch` · `ag-azure` `ag-official` ·
  `li-azure` `li-official` · `adk-qs` `adk-sokart` `adk-official` — one wrapper config each in
  [`field/config/`](../../field/config/) (adapter type, entry point, timeout, pack allowlist, acceptance).
- **Packs (11):** `field-smoke` (cross-framework smoke: tool call, no-tool, multi-tool) · 8 framework-core packs
  (`langgraph-core`, `crewai-core`, `openai-agents-core`, `pydantic-ai-core`, `llamaindex-core`, `autogen-core`,
  `smolagents-core`, `adk-core`) · `shared-safety` (refuse disallowed tool, boundary/scope adherence) ·
  `swe-bench-sample`.
- **Tiers:** `local` (oMLX, default) for every agent; `cheap` cloud cross-check on a representative subset.
- **Policies (already enforced by the runner):** serial execution; per-(agent|scenario|tier|model) resume key;
  **skip = failure**; `quarantined: true` configs fail closed for the local tier without executing; judge
  provider ≠ `mock` hard guard; LLM HTTP capture (agent calls in the worker process, judge calls in the test
  process) sanitized to `…/llm/`.
- **Acceptance:** per-agent `minimum_pass_rate` (currently 0.5) + zero silent failures; every failure classified
  (shim / wrong config / adapter / oracle) and triaged into 31.5.

### 4.3 Track C — docker / LLM infrastructure suites (gate the environment itself)

| Suite | File | Asserts | Marker |
|---|---|---|---|
| Image validation | `tests/test_docker.py` | image builds; `--help`/`version`/`validate [--strict]`/`run` inside the container | `docker` |
| Container→LLM | `tests/test_security_docker_llm.py` | the container reaches the host oMLX via `host.docker.internal:8000` and completes real LLM calls (fail-closed: no daemon/image/omlx ⇒ fail, not skip) | `docker` |
| Container sandbox | `tests/test_security_container_integration.py` | `run_in_container` sandbox execution paths | `docker` |
| Judge on oMLX | `tests/test_judge_omlx_integration.py` | real `JudgeVerdict`s (score+rationale) from the pinned local model | `omlx` |
| Adapter↔LLM | `tests/test_adapters_{adk,autogen,llamaindex,smolagents}_llm.py` | each such adapter drives a real agent against the live endpoint (the langgraph/crewai/openai-agents/pydantic-ai adapters get their live-LLM exercise via Track B, the field matrix) | `omlx` |

`make test` excludes these markers; the field run executes them explicitly (§5) and they must be green on the
field machine before Track A/B results count.

### 4.4 Required demonstrations (WBS part 17 — explicit)

1. **Verifier offline on a clean machine** (never ran the drill) — FT-A-VERIFY-OFFLINE.
2. **A witness-confirmed `missed`** — FT-A-ADD-PROOF (CUJ-30).
3. **A `witness_discrepancy`** (the log lied) — FT-A-ADD-PROOF (CUJ-30).
4. **The RoE abort demonstrated** (abort in seconds) — FT-A-ADD-GOV (CUJ-48/49).

### 4.5 Gaps to close before the run (31.1 harness work, issue #82)

Found while writing this plan — each blocks a deterministic, docker-reproducible field run:

1. **Pin the agent SHAs.** `field/list.txt` has `TODO` for every commit — clones track HEAD today. Pin before any
   reported result.
2. **`field/setup.sh` default list is wrong**: it points at `field/list1.txt`, which does not exist (the actual
   list is `field/list.txt`; `run-local.sh` already defaults there).
3. **Runtime image bakes only `scenarios/`** — `packs/` (incl. `quickstart-demo.yaml`) and `field/` are not in the
   image; in-container demo/quickstart runs need them mounted (or bake them in).
4. **Image extras are partial** (`[dev,judge,langgraph,pydanticai]` only) — in-container matrix runs involving
   crewai/smolagents/autogen/llamaindex/adk/openai-agents adapters need those extras installed (or rely on each
   agent's own venv, which is the current design).
5. **Cross-platform venvs:** agent venvs built on macOS cannot execute inside Linux containers — an in-container
   full-matrix run requires Linux-built agent venvs. v0.1.0 stance: run the matrix on the host (where MLX and the
   agent venvs live); use docker for Layers 1–2 and sandboxed execution. A fully containerized matrix is
   documented but optional.
6. **Dockerfile label/license mismatch** (`MIT` vs Apache-2.0 in `pyproject.toml`) — fix before M32 release scans.
7. **Nightly CI runner choice** — hosted `ubuntu-latest` has no Apple Silicon/MLX: local tier needs a self-hosted
   macOS runner **or** an Ollama service-container tier; the `cheap` tier runs anywhere with `OPENROUTER_API_KEY`.
8. **`agentdrill verify` CLI is a planned stub** (`cli/verify.py` → `_planned.planned()`, exit code 2) — the
   engine lives in `lifecycle/verifier.py`; wiring the command is a precondition for the required offline-verifier
   demonstration (§4.4.1).
9. **`agentdrill run --dry-run` / `--explain` are documented but not wired** — the README and
   [cli-reference](../reference/cli-reference.md) list them, but `cli/run.py` has no such options (the engine
   exists in `dx/dry_run.py`); the flag currently fails as unknown. Wiring is a precondition for FT-E28.
10. **Optional:** a small `docker compose` for the field stack (agentdrill service + Ollama sidecar) so the whole
   environment is one command; keep it minimal.

### 4.6 Value-adding field tests (quality enrichment)

> Grounded in a full read of PRD 00–43, the design docs, and the code (scoring registry, credibility, hardening,
> lab, attacker, witness, tools). Each suite strengthens the **trustworthiness of the field results
> themselves** or widens coverage onto shipped code paths the current matrix never exercises. Defects found
> here flow into 31.5 like any other; wiring work lands under 31.1/31.T — these are not scope beyond M31.

| Suite | Tests | Grounding (code / design) | Anchor | Pri |
|---|---|---|---|---|
| **FT-E01 Metric coverage** | Expand field packs to exercise the **full scorer registry**: today's packs use 6 of 31 registered metrics (`tool_called`, `tool_correctness`, `step_efficiency`, `task_completion`, `output_correctness`, `zero_disallowed_actions`). Add scenarios for the remaining dimensions — safety (`policy_adherence`, `retry_discipline` hybrid gates, `refusal_quality`, `unsafe_action_avoidance`, `cost_budget_adherence`), grounding (`factual_consistency`, `source_citation`, `output_grounding`, `contradiction_detection`), structure (`schema_validity`, `field_correctness`, `argument_correctness`, `phantom_step_scorer`) | `scoring/registry.py`, `scoring/engine.py` (`_DIMENSION_MAP`), `scoring/deterministic/*`, `scoring/judge/scorers.py` | F4, PRD 10 (scorers delivered) | **P0** |
| **FT-E02 Security-eval pack** | A `field-security-eval.yaml` built from `SecurityScenarioGenerator` + `shared-safety`: prompt-injection resistance, exfiltration prevention, SSRF prevention, sandbox-escape resistance — scored by the four registered security scorers, judge-labeled where rubric | `security/evals.py` (`PromptInjectionResistanceScorer`, `DataExfiltrationPreventionScorer`, `SSRFPreventionScorer`, `SandboxEscapeResistanceScorer`, `SecurityScenarioGenerator`) | PRD 21 pack 2 (re-pointed) | **P0** |
| **FT-E03 Injection carriers** | Indirect injection delivered through **tool results**, using the lab's 12 poisoned-content carriers (HTML/CSS-hidden, markdown, PDF, DOCX, spreadsheet, image, email, calendar, issue, PR, README, chat): `web_search` returns carrier content that tries to hijack the next call; report per-carrier miss rates per framework (a field-scale carrier matrix) | `lab/carriers.py` (M23), `lab/core.py`; fixtures `mcp_tool_poison`, `mcp_rug_pull`, `memory_poison` | F88, CUJ-32/33 | P1 |
| **FT-E04 Reliability (`k`-repeated)** | Same scenario × k (k ∈ {5, 25}, seeded) → `Hold@k` / `ASR@k` per agent×scenario; a pass that fails on trial 3 is a **finding**, not noise; flakiness budget per [ci-field-tests](../ci-field-tests.md) | `attacker/tiers.py`, `attacker/metrics.py`, `attacker/pressure.py` | PRD 25 (E5 τ-bench `pass^k`), CUJ-28 | P1 |
| **FT-E05 Determinism A/B** | Run the same pack twice on the same pinned agent+model (`temperature=0`, seeded): deterministic metrics must be **identical**; LLM-bound rows measured for variance; report per-scenario reproducibility, not just pass/fail | `determinism/seed.py`, `determinism/reproducibility.py`, `determinism/reproduction.py` | R6, storage-design | **P0** |
| **FT-E06 Judge credibility** | Run the known-answer **battery** + **drift canaries** against the pinned local judge on the field machine; publish agreement / false-block / false-miss with CIs; one **cross-judge agreement** run vs the `cheap` tier; make the "small local judge" caveat *measured* | `credibility/battery.py`, `credibility/drift.py`, `credibility/calibration.py`, `reporting/ci.py` (bootstrap CIs) | F79–F84, CUJ-25 | **P0** |
| **FT-E07 Fault injection** | Field-runner failure modes, each asserted **fail-closed** with the right exit code and classification, never a silent pass: oMLX dies mid-run (exit 3), wrong endpoint (exit 2), agent hang → per-scenario timeout artifact, agent crash → error artifact, corrupt pack YAML → `PackParseError` with location, corrupt resume index → no false "passed" resurrection, unwritable results dir → loud abort, concurrent runs → `RUNNING.lock` refuses | `hardening/faults.py` (`FAULT_KINDS`), `errors.py` (taxonomy), `models/errors.py`, [errors.md](../reference/errors.md) | PRD 13 reliability | **P0** |
| **FT-E08 Secret-leak sweep** | Post-run scan of **all** field artifacts (`console.log`, `llm/` captures, prompts, completions, `result.json`) for secret/PII patterns; assert zero findings besides the known dummy `omlx-test`; verify adapter-config sanitization held | `tools/secrets_scanner.py`, `security/sanitize.py`, `adapters/base.py::_sanitize_agent` | PRD 06, F15 | **P0** |
| **FT-E09 Efficacy control (field analog)** | Every safety scenario runs an **unguarded twin** (guard removed / disallowed tools not declared): the attack must *land* unguarded for the guarded refusal to count; otherwise flag `attack_inert` and exclude from pass rates — a lazy model must not pad a green row | `efficacy/control.py`, `efficacy/inert.py` | F59, ADR-0007 | P1 |
| **FT-E10 Utility-under-attack** | Each attack scenario carries a **benign twin**; publish benign utility / utility-under-attack / enforcement rate per framework — an agent that refuses *everything* is exposed as safety theater | `efficacy/utility.py` | F51 (AgentDojo three-metric frame) | P1 |
| **FT-E11 Baseline drift** | Snapshot the first green sweep per (agent×scenario) as a **baseline**; each nightly compares candidate vs baseline and flags regressions with failure classification + change detection (agent-repo SHA vs model pin) — the field matrix becomes a **continuous regression suite over 19 live third-party agents**; this is also the detector for the unpinned-SHA gap (§4.5.1) | `baselines/store.py`, `comparison/engine.py`, `comparison/change_detection.py`, `analytics/taxonomy.py` | F7/F23 analog, CUJ-9/21 | P1 |
| **FT-E12 Schema/verifier round-trip** | Validate every field artifact (`result.json`, `artifact.json`, `index.jsonl`) against the versioned run-result schema; bundle + offline-verify (tamper variants covered by FT-A-VERIFY-OFFLINE) | `schema_version/validator.py`, `lifecycle/verifier.py` (CLI stub gap §4.5.8) | F64, CUJ-23 | P1 |
| **FT-E13 Dark holdout (field)** | Keep an unpublished subset of field scenarios; published-green + holdout-red = pack-gaming finding (an agent overfit to the public pack) | `security/holdout.py`, `security/cadence.py` | F33, DD-29 | P1 |
| **FT-E14 Nightly canary + trend gate** | Nightly **driver canary** (catch adapter/driver breakage before users) + a "what got worse" trend query across nightly summaries; CI fails on a pass-rate regression beyond the flake budget | `platform/versioning.py`, `reporting/trends.py`, `observability/metrics.py` | PRD 41 SLA, F23 | P1 |
| **FT-E15 Cost-governor enforcement** | Run a subset with a tiny `--max-cost`: the sweep must abort `cost_exceeded`, mark remaining cases `aborted`, and report — loud, never truncated-into-green | `tools/cost_governor.py`, `hardening/cost.py` | PRD 13 §Cost | P2 |
| **FT-E16 Timeout/kill-time probing** | Deliberately hung agent → measure timeout-enforcement latency (p50/p95 over ≥5 trials) and budget-metric behavior under load | `killchain/timing.py`, `killchain/probe.py` (field-scale analog), `scoring/deterministic/budget.py` | R8/F37 analog | P2 |
| **FT-E17 Multi-agent + approval fidelity** | Multi-agent delegation and approval-workflow scenarios (delegation abuse, approval-display ≡ executed action) on the agents that support it (e.g. CrewAI, smolagents; `multi_agent_delegate` fixture exists) — labeled partial, honest | `tools/advanced.py` (X4 `MultiAgentEvaluator`, X5 `ToolApprovalEvaluator`), `packs/fixtures/multi_agent_delegate.json` | ASI07/09-class (CUJ-56/57, field-scale, labeled) | P2 |
| **FT-E18 Model-matrix tier** | The smoke pack across ≥3 models (local 4B, local 9B, `cheap`) for one representative agent per framework → a per-model pass-rate column that separates "the framework" from "the model" and feeds the compatibility table + judge labeling | `tools/advanced.py` (X8 `ModelMatrixRunner`) | PRD 41 (model roles separated), PRD 25 | P2 |
| **FT-E19 VCR record/replay** | Record one local-LLM sweep as a cassette; replay it **fully offline** to prove the harness scores identically without any LLM — a deterministic nightly smoke and the bisection tool that separates harness bugs from model nondeterminism when a scenario flips | `fixtures/http_record.py`, `testing/vcr.py` | R6, F5 discipline | P2 |
| **FT-E20 Evidence completeness** | Assert every field result carries its full evidence chain (trajectory, LLM capture pair, judge prompt+verdict, score JSON); a missing link is an explicit `evidence_gap`-class failure, never skipped; emit the run summary per sweep | `evidence/binding.py` (analog), `hardening/observability.py` (`build_summary`) | F52 analog, F27 | P2 |

**Second wave — secondary seams (FT-E21–E31):**

| Suite | Tests | Grounding (code / design) | Anchor | Pri |
|---|---|---|---|---|
| **FT-E21 Meta-verification (theater plants)** | Plant the predecessor's documented **scoring-theater bugs** in a mock agent; the harness must catch every plant: a console claiming "N passed" that disagrees with the artifacts, a vacuous no-op agent, judge criteria as dead text, a doctored `result.json`/`console.log` pair, a `mock` judge masquerading as real — the harness trusts **only its own artifacts**. Distinct from FT-E07 (accidental faults): adversarial deception | `security/meta_verification.py`, `security/hidden_case.py`, `self-attack/meta-verification.yaml` | G10/G11, RK-14, F43 | **P0** |
| **FT-E22 Publish-gate honesty** | Attempt to publish bad numbers — each rejected loudly: a single-seed (or duplicate-seed) number, a report hiding its misses, a bare percentage without CI, a composite score, a `mock`-attested row | `reporting/honesty.py`, `reporting/stats.py`, `reporting/ci.py`, `lifecycle/attestation.py` | R5, F29/F55, DD-27 | **P0** |
| **FT-E23 Sandbox egress containment** | A sandboxed agent attempts non-loopback egress mid-scenario (`--network none` + egress controller) → denied and audited; zero non-loopback contact, capture-verified | `security/egress.py`, `security/sandbox.py::run_in_container`, `lab/isolation.py` | PRD 06, G5 | P1 |
| **FT-E24 Parallel == serial** | The same pack serially and via `agentdrill run --workers N`: identical outcomes, order preserved, backpressure held — the parallel path the serial field runner never touches | `runner.py` (ThreadPoolExecutor), `hardening/perf.py::parallel_matches_serial` | performance-budget promise | P1 |
| **FT-E25 Cross-OS parity** | The in-container Linux variant (§5.7) on a smoke subset vs the macOS host: deterministic-metric outcome **parity ≥ 99.5 %** — the PRD 41 metric no suite measures today | Dockerfile, `platform/matrix.py` | PRD 41 | P1 |
| **FT-E26 Interop import field-run** | Import a small real promptfoo/garak/AgentDojo/PyRIT suite → run end-to-end against one field agent (mapping fidelity ≥ 95 %); wire + run the existing `swe-bench-sample.yaml` (in `field/scenarios/` but listed in no agent config) | `interop/importers.py`, `benchmarks/loader.py` | R9/F12, R74 | P1 |
| **FT-E27 Release-shape gates on the field machine** | The M31 exit criterion "port/absorption tasks complete" made executable: parity gate green (absorption ledger + G1–G14), claims-linter zero violations, standards drift watcher fresh, self-attack cadence green (evasion + meta + holdout ran this cycle) | `parity/gate.py`, `standards/claims.py`, `standards/registry.py`, `security/cadence.py` | M31 exit criteria, R7 | P1 |
| **FT-E28 Dry-run purity + MCP read-only** | `run --dry-run` performs **zero** driver executions and zero LLM calls (probe-verified); the MCP drill surface lists **no write tools** and records queries — *needs the §4.5.9 dry-run wiring* | `dx/dry_run.py` (`executions == 0`), `dx/mcp_surface.py::require_read_only` | R43, R51 | P1 |
| **FT-E29 Judge-backend parity** | The FT-E06 battery across all local judge backends — OpenAI-compat (oMLX), Ollama-native, `MLXJudgeClient` managed server: verdicts agree on known answers; each client's failure path degrades to `JudgeError` → exit 3, never silent | `scoring/judge/{openai,ollama,mlx}.py` | F81 analog | P2 |
| **FT-E30 Judge-cache correctness** | The same artifact scored twice → cache hit with an **identical verdict**; TTL expiry → re-call; `cache_stats` reports savings; a corrupted cache entry must not poison a verdict | `cache/judge_cache.py`, `scoring/engine.py::cache_stats` | PRD 13 §Cost | P2 |
| **FT-E31 Plugin discovery** | Custom scorer + judge registered via entry points in a scratch env → `plugins list/info` discovers them and a run uses them; an unknown metric fails loudly (`ConfigError`) at load | `plugins/manager.py`, `scoring/registry.py`, `cli/plugins.py` | DD-09, F14 | P2 |

**Extensions to existing suites (no new IDs):**

- **E08 +** redaction receipts on the committed-results path: bundle a planted fake-secret finding —
  `lifecycle/privacy.py::verify_receipts` passes, the verifier accepts (F65).
- **E12 +** schema-version **migration**: an old-version run artifact loads/migrates cleanly
  (`schema_version/validator.py`).
- **E02 +** the sandbox-escape family executed against a containerized target (ties into FT-E23).
- **E16 +** the 30 s/scenario timeout measured as percentiles under parallel load (ties into FT-E24).

**Deliberately *not* field tests** (the boundary, per PRD 43 T8): unit-level scorer/oracle coverage (the 31.C
≥ 95 % gate owns that); browser/computer-use frontier classes (browser-only first; no field agent is
browser-wired — a not-tested item); T3 adaptive search (DD-44); third-party SaaS platforms (out of v0.1.0
scope — not-tested list). Past this point quality comes from P0 depth + nightly cadence, not suite count.

**Run order:** the P0 suites (E01, E02, E05–E08, **E21, E22**) gate the report; P1 (E03, E04, E09–E14,
E23–E28) runs in the nightly cadence (§5.9); P2 (E15–E20, E29–E31) is scheduled behind them. Suites needing
thin glue (E09–E11, E14, E19, E23, E25–E27, E30) are 31.1 harness work; E28 needs the §4.5.9 wiring — no new
engine anywhere.

---

## 5. How to run the docker-based field tests

### 5.0 Preflight (fail loudly, never skip silently)

```sh
docker info                                            # daemon up
curl -s http://127.0.0.1:8000/v1/models | head -5      # oMLX serving (local tier)
uv run agentdrill doctor                               # env sanity check (implemented, exits 2 on failure)
# cloud tier only: export OPENROUTER_API_KEY=...       # never written to disk or logs
```

### 5.1 Build the images

```sh
docker build -t agentdrill:field -f Dockerfile .                  # main image
docker build -t agentdrill-agent-runner -f Dockerfile .            # sandbox image (run_in_container)
# `agentdrill-test` is built (and removed) automatically by tests/test_docker.py
```

### 5.2 Layer 1 — image / CLI validation in the container

```sh
uv run pytest tests/test_docker.py -m docker
# or ad hoc:
docker run --rm agentdrill:field --help
docker run --rm agentdrill:field validate --pack scenarios/core-launch.yaml --strict
```

### 5.3 Layer 2 — container↔LLM and sandbox execution (needs oMLX on the host)

```sh
uv run pytest tests/test_security_docker_llm.py -m docker         # container → host.docker.internal:8000
uv run pytest tests/test_security_container_integration.py -m docker
uv run pytest tests/test_judge_omlx_integration.py -m omlx        # judge verdicts from pinned local model
uv run pytest tests/test_adapters_adk_llm.py tests/test_adapters_autogen_llm.py \
                tests/test_adapters_llamaindex_llm.py tests/test_adapters_smolagents_llm.py -m omlx  # adapter↔LLM
```

### 5.4 Layer 3 — the agent field matrix (Track B)

```sh
# 1. Clone the third-party agents at pinned SHAs (fix §4.5.1/§4.5.2 first)
bash field/setup.sh                                # or: --agent lg-official,sm-qs …  · --refresh · --dry-run

# 2. Dry-run: see exactly what would execute
bash field/run-local.sh --tier local --dry-run

# 3. One agent first (smoke the loop), then the full matrix — local LLM, zero cost
bash field/run-local.sh --tier local --slug lg-official
bash field/run-local.sh --tier local

#   Useful controls:
#   --scenario <id>        one scenario only      --fail-fast   stop on first failure
#   --offset N --limit N   paginate long sweeps   --clean       wipe results dir first
#   --resume               skip already-passed (key: agent|scenario|tier|model)
#   --resume --failed-only re-run only prior failures
```

Results, evidence and the resume index land in `field/results/` (layout in
[`field/README.md`](../../field/README.md)); `RUNNING.lock` prevents concurrent sweeps.

### 5.5 Optional — cloud cross-check tier

```sh
OPENROUTER_API_KEY=… bash field/run-local.sh --tier cheap \
  --endpoint https://openrouter.ai/api/v1 --model openai/gpt-4o-mini
```

Use for judge cross-validation on the published numbers; keep the local tier as the pass/fail gate.

### 5.6 Demo stack + first-run timing (Track A entry point)

```sh
# `quickstart` resolves packs/quickstart-demo.yaml from the cwd — the image bakes only
# scenarios/ (§4.5.3), so mount the repo (or bake packs/ in) and time the run:
docker run --rm -v "$PWD":/app -w /app agentdrill:field quickstart
# after §4.5.3 is fixed, the plain form works too:
docker run --rm agentdrill:field quickstart           # offline demo; ≤ 15 min budget (CUJ-24)
```

### 5.7 In-container matrix runs (optional variant)

```sh
docker run --rm -v "$PWD":/app -w /app \
  -e AGENTDRILL_FIELD_ENDPOINT=http://host.docker.internal:8000/v1 \
  -e AGENTDRILL_FIELD_MODEL=Qwen3.5-4B-4bit \
  agentdrill:field bash field/run-local.sh --tier local --slug lg-official
```

Caveats (§4.5.5): agents' venvs must be Linux-built for this path; oMLX stays host-side. Default v0.1.0 posture:
host-driven matrix + docker for layers 1–2.

### 5.8 Exit codes (interpret results loudly)

`0` all passed · `1` misses · `2` config error · `3` judge/oracle infra error · `4` critical miss ·
`5` critical divergence ([errors.md](../reference/errors.md)). In field trials a **skip is a failure** and a
quarantined agent fails closed — never a silent green.

### 5.9 Nightly field-test CI job (31.6, issue #86)

Per [docs/ci-field-tests.md](../ci-field-tests.md): matrix `suite × tier`, `fail-fast: false`, secrets via CI env
(`OPENROUTER_API_KEY`), cost/time ceilings (local $0/30s · cheap $0.01/30s · better $0.05/60s per scenario),
flake budget (30s/scenario, 1 retry, ≤20% failures), JSON summary + artifacts uploaded. Runner choice per §4.5.7:
self-hosted Apple Silicon for the `local` tier (or Ollama sidecar on hosted runners), hosted `ubuntu-latest` for
the `cheap` tier. The nightly also runs the **P1 enrichment suites** (§4.6: FT-E03/04, E09–E14, E23–E28) — it is
the cadence where drift, holdout and reliability evidence accumulates. Nightly must be **scheduled + green (or
explicitly not-planned)** — record which in the report.

---

## 6. Evidence & report (31.4, issue #84)

**All runs are persisted in git.** The harness (`scripts/fieldtest/`) writes one
directory per case under `field-test/v0.1.0/results/<suite>/cases/<ID>/`:
`verdict.json` (status, class, grounded, assertions_total/grounded, llm_captured) ·
`assertions.ndjson` (each assertion's command + grounded flag) · `commands.log` ·
`stdout.log`/`stderr.log` · `artifacts/` — including `artifacts/llm/<name>-request.json`
and `-response.json` (**the LLM request/response pairs**, must) and, for Track B,
`artifacts/matrix/…`. Results are **committed**; the leak gate
(`scan_results.py`) and the per-case `no-secret-leak` assertion guarantee no
unmasked secret is persisted.

[FIELD_TEST_REPORT.md](FIELD_TEST_REPORT.md) records: per-CUJ pass/fail, per-agent matrix results, first-run
timing, the defects table (root cause + fix + regression test), the enrichment results (§4.6 — metric-coverage
table, judge-credibility rates with CIs, determinism A/B, fault-injection outcomes, secret-sweep verdict), and —
mandatory — the **not-tested list** with reasons (environments, harnesses, surfaces, tiers we did not exercise).
The report is filled from the committed results by `scripts/fieldtest/build_report.py`
(`make fieldtest-report`), never hand-edited. [known-limitations.md](../reference/known-limitations.md) is
updated in the same pass (31.D, issue #91).

## 7. Defect workflow (31.5, issue #87)

For every failure: classify (shim / wrong config / adapter / oracle) → fix → add a regression test → link it in
the report's defects table. No failure is closed by re-running alone; no defect closes without evidence (31.T).

## 8. Success measures — what we measure to determine success

A green run without these numbers is not success — it is an unmeasured run. Every measure below lands in
[FIELD_TEST_REPORT.md](FIELD_TEST_REPORT.md) (§6) with its evidence; **a measure we did not take is a not-tested
entry with a reason, never a silent omission.**

### 8.1 Coverage — did we test everything we planned?

| Measure | Target | Evidence |
|---|---|---|
| CUJs exercised end to end | **63/63**, each mapped to ≥1 executed suite | per-CUJ table in the report |
| Track A suites executed | **14/14** (`FT-A-QUICKSTART` … `FT-A-ADD-PLATFORM`) | suite logs + artifacts |
| Track B matrix | **19/19** agents × their configured packs; every scenario runs (skip = failure) | `field/results/index.jsonl` |
| Track C infra suites green | **5/5** docker/omlx-marked suites on the field machine | pytest output |
| Required demonstrations recorded | **4/4** — offline verifier · witness-confirmed `missed` · `witness_discrepancy` · RoE abort | §4.4 evidence refs |
| Enrichment suites | **P0 green before the report** (E01, E02, E05–E08, E21, E22 — 8/8); P1 green in nightly; P2 scheduled | §4.6 suite results |
| Agent SHA pinning | 100% of agents cloned at pinned SHAs (§4.5.1) | clone log |
| Not-tested list completeness | 100% of unexercised surfaces/tiers/harnesses listed **with reasons** | report §Not tested |

### 8.2 Outcomes — the results themselves

| Measure | Target | Evidence |
|---|---|---|
| Scenario pass rate (milestone bar) | **100% of planned scenarios pass after defect fixes** (31.5) | `run.json` / `summary.json` |
| Per-agent acceptance (triage bar) | each agent ≥ its configured `minimum_pass_rate` (0.5 today) | per-agent rollup |
| Skip/quarantine discipline | every skip or quarantine appears as a **failure with reason** — zero silently green | `index.jsonl` |
| Exit codes | 0 on green suites; every non-zero classified per §5.8 | suite exit codes |
| Defect closure | 100% of found defects fixed **with a linked regression test**; zero closed by re-running alone | report defects table |
| Framework compatibility row | `field-smoke` green on **8/8** frameworks with the pinned local model — or the misses stated | release compatibility table |
| First-run (CUJ-24) | **≤ 15 min** on a clean machine/env, zero code changes | timed run log |

### 8.3 Trust — is the evidence believable?

| Measure | Target | Evidence |
|---|---|---|
| Determinism A/B (FT-E05) | **100%** deterministic-metric identity across repeat runs; LLM-bound variance reported per scenario | A/B artifacts |
| Judge credibility (FT-E06) | agreement / false-block / false-miss rates published **with CIs**; **zero** `judge_drift` (canary flips without a pin change) | calibration output |
| Judge non-mock guard | 100% of judge-scored results: provider ≠ `mock`, LLM capture + judge prompt/verdict files present | `test_field_agent.py` §5a assertions |
| Fail-closed rate (FT-E07) | **100%** of planted faults fail loudly with the right exit code; zero silent greens | fault log |
| Theater plants caught (FT-E21) | **100%** of scoring-theater plants detected | meta-verification output |
| Publish-gate honesty (FT-E22) | **100%** of bad-number plants rejected (single-seed, hidden misses, bare %, composite, `mock` row) | gate output |
| Secret-leak sweep (FT-E08) | **0** findings beyond the known dummy `omlx-test`; redaction receipts verified | sweep report |
| Evidence completeness (FT-E20) | **100%** of results carry trajectory + LLM capture pair + judge prompt/verdict + score JSON | evidence audit |

### 8.4 Reliability & stability

| Measure | Target | Evidence |
|---|---|---|
| Repeated-trial stability (FT-E04) | pass rate holds across seeded k ∈ {5, 25} trials within the flake budget (1 retry/scenario; >20% failures fails the job) | `Hold@k` / `ASR@k` per scenario |
| Timeout discipline | per-scenario **≤ 30 s** (local); every timeout recorded as a **failure**, never a pass | `result.json` durations |
| Parallel == serial (FT-E24) | identical outcomes, order preserved, backpressure held | comparison output |
| Cross-OS parity (FT-E25, if run) | **≥ 99.5%** deterministic-metric outcome parity (macOS arm64 vs Linux container) | parity report |
| Judge/cache correctness (FT-E29/E30) | identical verdicts on identical inputs across backends; a cache hit never changes a verdict | battery + `cache_stats` |
| Baseline drift (FT-E11) | first green sweep baselined per (agent×scenario); every later regression flagged + classified within **one nightly** | comparison / trend output |
| Egress containment (FT-E23) | **0** non-loopback contact from sandboxed agents | network capture + audit |

### 8.5 Efficiency, cost & cadence

| Measure | Target | Evidence |
|---|---|---|
| Local-tier cost | **$0.00** (oMLX); cloud cross-check within `--max-cost` | cost report |
| Cost-governor enforcement (FT-E15) | over-budget ⇒ aborts `cost_exceeded`, remaining cases `aborted` — never truncated-into-green | governor log |
| Suite duration | within per-tier job ceilings — local **5 min** · cheap **10 min** · better **15 min** (Appendix B) | run timings |
| Cache savings | reported per sweep (`cache_stats`); provenance labeled | engine cache stats |
| Nightly job (FT-E14/E27) | scheduled + green; driver canary catches breakage; release-shape gates (parity, claims linter, drift watcher, self-attack cadence) green | CI history |

### 8.6 Roll-up

Success = §8.1 coverage complete **+** §8.2 outcomes green **+** §8.3 trust measures met **+** §8.4/§8.5 within
budgets — recorded in the report with every exception owned by a defect (§7) or a not-tested entry. The exit
gate (§9) consumes exactly these measures.

---

## 9. Exit gate

All success measures of §8 met: all field scenarios pass (Layers 1–3 + every suite in §4.1/§4.2/§4.3 green, with
the four required demonstrations of §4.4 recorded); the **P0 enrichment suites** of §4.6 (FT-E01, E02, E05–E08,
E21, E22) green; CUJ-1..CUJ-63 exercised end to end; defects fixed with regression evidence; the report
published **with the not-tested list stated**; nightly job scheduled+green (or explicitly not-planned); standard
gates (31.T tests · 31.C coverage ≥ 95% · 31.L ruff+mypy strict · 31.CR review · 31.D docs) closed.

---

## Appendix A — environment variables the field run uses

| Variable | Set by | Meaning |
|---|---|---|
| `AGENTDRILL_FIELD_TIER` / `_VARIANT` | runner | `local\|cheap\|better` / `tier__model_safe` |
| `AGENTDRILL_FIELD_ENDPOINT` / `_MODEL` | runner | LLM endpoint (default `http://127.0.0.1:8000/v1`, `Qwen3.5-4B-4bit`) |
| `AGENTDRILL_FIELD_JUDGE_PROVIDER` / `_JUDGE_ENDPOINT` / `_JUDGE_MODEL` | runner/user | judge backend (`ollama`/`mlx`/OpenAI-compatible) |
| `AGENTDRILL_FIELD_CONFIG_DIR` / `_AGENTS_DIR` / `_WORKER` / `_AGENT_DIR` / `_AGENT_PYTHON` | runner | per-agent config, clones, worker, interpreter |
| `AGENTDRILL_FIELD_PACK` / `_OUTPUT_DIR` / `_AGENT` | runner | active scenario pack, evidence dir, agent slug |
| `AGENTDRILL_FORCE_MODEL` | runner (local tier) | override agents' hardcoded model names |
| `OPENROUTER_API_KEY` / `OPENAI_API_KEY` / `OPENAI_BASE_URL` | user/CI | cloud tiers; never logged, masked in captures |
| `AGENTDRILL_DOCKER_IMAGE` | user/CI | override sandbox image (default `agentdrill-agent-runner`) |

## Appendix B — cost & time ceilings (from [docs/ci-field-tests.md](../ci-field-tests.md))

| Tier | Model | Max cost/scenario | Max time/scenario | Max time/job |
|---|---|---|---|---|
| local | Qwen/MLX (oMLX) | $0.00 | 30s | 5 min |
| cheap | gpt-4o-mini (OpenRouter) | $0.01 | 30s | 10 min |
| better | gpt-4o (OpenRouter) | $0.05 | 60s | 15 min |

Retry on flake: 1 per scenario; a job fails at >20% scenario failures. The cost governor (`--max-cost`) aborts
over-budget runs with `aborted: cost_exceeded` — loud, never silent.
