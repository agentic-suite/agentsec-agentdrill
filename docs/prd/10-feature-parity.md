# PRD 10 — Feature Parity (Absorption of the predecessor projects)

**BLUF:** agentdrill absorbs **the red-team predecessor idea** (the adversarial-testing idea) and the eval-harness
mechanics of the shipped/retired **predecessor eval harness (retained privately)**. This document is the row-by-row ledger: every
absorbed capability is **delivered**, **delegated** (to another ecosystem tool, on purpose), or
**waived** (not applicable to a proof harness for defenses).

**Status:** Draft — v0.1.0 (2026-10-09) · **Owner:** @deghosal-2026 · **Parent:** agentsec-ecosystem #209

## A. From the predecessor eval harness (eval-harness mechanics)

| Absorbed capability | Disposition | Where in agentdrill |
|---|---|---|
| Scenario pack format (YAML, `pack` + `scenarios[]`) | **Delivered** | Attack-pack format (PRD 15) — pack/cases, `incident_ref`, target, oracle |
| Expected-answer types (`exact`/`schema`/`tool_trace`/`rubric`) | **Delivered** | Oracle types: `blocked`/`missed`/`degraded` decided by deterministic oracle or judge |
| Agent adapter contract (subprocess / python / HTTP) | **Delivered** | Driver adapters (same invocation-payload + run-envelope contract) |
| 12 framework adapters (LangGraph, PydanticAI, CrewAI, OpenAI Agents, smolagents, AutoGen, LlamaIndex, Claude, ADK) | **Delegated** | v0.1.0 uses promptfoo/garak interop + ≥2 Tier-1 harness drivers; frameworks return as packs (in-scope target) |
| Trajectory capture (`steps`: tool_call/tool_result/response) | **Delivered** | Attack trajectory (attempt ↔ stack response ↔ evidence) |
| Deterministic scorers (17) | **Delivered** (subset) | Deterministic oracles: deny/allowed, confinement, budget, sequence, grounding |
| LLM-as-judge metrics (11) | **Delivered** (subset) | Judge oracles for qualitative cases (refusal quality, explanation adequacy) |
| Hybrid scoring (deterministic gate + judge fallback, offline-safe) | **Delivered** | Oracle engine (`judge_not_evaluated` offline) |
| Evaluation hierarchy (safety > correctness > efficiency) | **Delivered** (re-pointed) | enforcement > integrity > efficiency |
| Three-gate dimensions (compatibility/safety/quality) | **Delivered** (re-pointed) | compatibility / enforcement / integrity |
| Scoring breakdown + divergence (critical/warning) | **Delivered** | Divergence classification + `--fail-on-divergence critical` |
| Failure taxonomy (`FailureTaxonomy`) | **Delivered** (re-pointed) | `safety_miss`, `policy_miss`, `evidence_gap`, `kill_slow`, … |
| Explicit golden baselines | **Delivered** | Golden expected results per pack version |
| Comparison engine (per-scenario / tag / aggregate; adapter/model-change detection) | **Delivered** | Coverage/regression diff across stack + pack versions |
| Three-way outcome classification | **Delivered** (re-pointed) | blocked / missed / degraded (+ target_error/agent_crash) |
| CI integration (`--ci`, exit codes, `$GITHUB_STEP_SUMMARY`, GH/GitLab) | **Delivered** | CI surface (F9) |
| Entry-point/plugin registry (custom scorers/adapters) | **Delivered** | Custom oracles + target/driver adapters (F14) |
| Fixture system + ToolStub (record/replay, `--live`) | **Delivered** | Deterministic attack fixtures (F5) |
| Run manifest (OS/arch/python/deps/agent) | **Delivered** | Reproducibility manifest (F6) |
| Adapter manifest + SHA-256 digest binding | **Delivered** | Target/driver digest bound to results |
| Sandbox mode (env stripping, FS isolation, Docker network) | **Delivered** | Untrusted-pack sandbox (PRD 06) |
| Trust policies (`trust` → adapter/tool matrix) | **Delivered** | Trust levels `built-in`/`local`/`external` (F14) |
| Audit trail (append-only policy log) | **Delivered** | Per-run audit (PRD 06) |
| Secret sanitization (key-name + regex redaction) | **Delivered** | Artifact/log redaction (PRD 06) |
| Pre-flight validation (`--pre-flight --strict`) | **Delivered** | Pack/target pre-flight |
| Parallel execution (`--workers`, `--max-outstanding`) | **Delivered** | Parallel pack execution |
| Caching (judge/run/schema) | **Delivered** | Oracle/judge cache |
| External benchmark connectors (SWE-bench/WebArena) | **Re-pointed** | Interop importer: promptfoo/garak/AgentDojo/PyRIT (F12) |
| pytest plugin | **Delivered** | `agentdrill test run` |
| HTML/Markdown reports | **Delivered** | Reporter (F8) |
| Two-layer defense model (deterministic vs judge) | **Delivered** (reframed) | Oracle discipline (PRD 02) |
| `pytest for agents` / release-discipline product DNA | **Delivered** (re-pointed) | `pytest for agent defenses` (PRD 05) |
| **Primary purpose: grade agent quality** | **Waived** | Out of scope — agentdrill proves *defenses*, not agent quality |
| Auto-prompt optimization | **Waived** | Never in scope |
| Model-quality leaderboard | **Waived** | Non-goal (PRD 14) |

## B. From the red-team predecessor idea

| Absorbed capability | Disposition | Where |
|---|---|---|
| Adversarial testing of agent defenses | **Delivered** | The whole product |
| Continuous (not point-in-time) red-team | **Delivered** | CI gate + per-release cycles (R3, R7) |
| Attack library / pack framing | **Delivered** | Attack-pack catalog (F1) |
| Novel exploit development | **Waived** | Non-goal — replay documented patterns only (PRD 14) |

## C. Parity gate

The v0.1.0 release must show this ledger with **no capability silently dropped**: delivered → tested,
delegated → a named tool/roadmap row, waived → a stated reason. Waived items are **by design**, not gaps.
See [PRD 12](12-traceability.md) for the requirement→feature→test mapping.
