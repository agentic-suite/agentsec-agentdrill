# PRD 03 — Landscape

**BLUF:** The attack tooling the ecosystem needs already exists (PyRIT, garak, promptfoo, AgentDojo,
InjecAgent) but is **offline and point-in-time** — it red-teams a snapshot, not a live policy stack. The
whitespace is a **continuous regression suite for security configuration** with public, reproducible,
honest results. agentdrill fills it by absorbing the eval-harness mechanics of the retired
**the predecessor harness** and re-pointing them at deployed defenses.

**Status:** Draft — v0.1.0 (2026-10-09) · **Owner:** @deghosal-2026 · **Parent:** agentic-suite #209

## Existing tools

| Tool / repo | Strength | Gap agentdrill addresses |
|---|---|---|
| **PyRIT** (Microsoft) | Rich red-team orchestration, LLM attack automation | Offline, point-in-time; no CI regression gate; no "drill your deployed stack" |
| **garak** | Broad LLM probe library, many probes | Probes models, not deployed agent *controls*; no reproducible per-stack result |
| **promptfoo** | Practical eval/red-team CLI, CI-friendly | Eval/red-team of prompts and models; not incident replay against deployed enforcement |
| **AgentDojo** | Rigorous agent-injection benchmark, ASR record | Research benchmark; not a per-stack regression suite; not a CI gate |
| **InjecAgent** | Attack dataset + ASR evidence | Dataset/research; not a continuous proof loop |
| **the predecessor eval harness (retired, retained privately)** | Shipped eval **harness** — scenario packs, adapters, deterministic+judge scoring, baselines, CI exit codes | Graded *agent quality*; no adversarial incident replay, no deployed-stack targets, no honest public defense benchmark |

## The whitespace

No tool converts red-team tooling from *"tooling for researchers"* into a **security-config regression
suite**: run the attacks that actually happened against your **deployed** config, gate policy PRs, publish
honest per-release numbers (misses included), and verify **kill-time**, not just detection. The ecosystem's
coverage map marks this row OSS-led and unowned.

## Migration from the predecessor harness

the predecessor harness is retired and superseded; its mechanics are absorbed (see
[PRD 10](10-feature-parity.md)). For anyone who used the predecessor harness:

| the predecessor harness concept | agentdrill equivalent |
|---|---|
| Scenario pack / case | Attack pack / attack case |
| Agent adapter (subprocess/python/HTTP/12 frameworks) | Driver adapter + target adapter (deployed stack) |
| Trajectory capture | Attack trajectory |
| Deterministic scorers + LLM judge | Oracles (deterministic first, judge where needed) |
| Golden baseline | Golden expected result (per pack version) |
| Regression comparison | Coverage/regression diff (stack + pack versions) |
| `--fail-on compatibility\|safety\|quality` | `--fail-on compatibility\|enforcement\|integrity` |
| Exit codes 0/1/2/3/4/5 | Gate exit codes (see [PRD 02](02-architecture.md)) |
| the predecessor store artifacts | `.agentdrill/` artifacts |

The predecessor's product philosophy ("stop unsafe agent changes from shipping", `pytest` mental model,
explicit golden baselines, local-first/CI-second, safety > correctness > efficiency) is preserved and
re-pointed in [PRD 05](05-features.md).

## Adjacent category notes

- **Not an observability product** — that is agentwatch (agentdrill *consumes* it).
- **Not an enforcement product** — that is agentpolicy / agentgate / agentkeys / agentseatbelt /
  agentkernel / agenthalt (agentdrill *drives* them).
- **Not a benchmark leaderboard for models** — the benchmark is *defenses vs. documented attacks*, with
  misses published.
