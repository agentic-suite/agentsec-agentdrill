# PRD 02 — Architecture

**BLUF:** agentdrill is a **runner + oracle + evidence pipeline** that executes curated, versioned
**attack packs** against a **deployed** agent-security stack and publishes reproducible, honest results.
It owns **no enforcement** — it exercises the enforcement other ecosystem tools provide. It inherits the
eval-harness mechanics of **the predecessor harness** (scenario packs, adapter contract, trajectory capture,
deterministic + judge scoring, baselines, comparison, CI exit codes, sandbox/trust/audit) and re-points
them from *"did the agent get better?"* to *"does the defense actually stop this documented attack?"*

**Status:** Draft — v0.1.0 (2026-10-09) · **Owner:** @deghosal-2026 · **Parent:** agentsec-ecosystem #209

## Where agentdrill sits

agentdrill is the ecosystem's **proof layer** and is deliberately thin: it produces attacks, observes what
the deployed stack does, and reports. It never becomes an enforcement point.

```
                        ┌──────────────────────────── agentdrill ────────────────────────────┐
 attack pack (YAML) ──► │  pack loader → case runner → target/driver adapters → oracles →       │
                        │  honest reporter → CI exit code → public benchmark                   │
                        └───────────────┬──────────────────────────────┬─────────────────────┘
                                        │ drives (attack)               │ reads evidence
                                        ▼                               ▼
             ┌──────────────────────────────── deployed stack ────────────────────────────────┐
             │ agentgate (MCP proxy) · agentkeys (broker) · agentseatbelt / agentkernel         │
             │ (confinement) · policyweave output (compiled policy) · agenthalt (halt/revoke) ·  │
             │ agentwatch (records + security events)                                            │
             └───────────────────────────────────────────────────────────────────────────────────┘
```

- **Targets** are the *real* enforcement path — agentgate, agentkeys, agentseatbelt/agentkernel,
  policyweave-compiled policy, agenthalt — **not** a simulation sandbox (requirement R2).
- **Evidence** is read from **agentwatch** (record + security-event schema), so drills produce the same
  machine-consumable artifacts every other tool consumes.
- **Kill-time** is measured by driving agenthalt/agentkeys and timing revocation, not by inferring it.

> **Analogy, borrowed from the predecessor harness:** the predecessor's two-layer defense observed an agent through an
> **adapter contract** and never modified it. agentdrill likewise observes *defenses* through a **target
> contract** and never enforces. If a drill needed to enforce to run, it would be testing agentdrill, not
> the user's stack.

## Components (v0.1.0)

1. **Attack-pack catalog + format** — versioned YAML packs; each case is an attack step bound to a deployed
   target and an oracle. Reuses the predecessor harness scenario-pack shape (see [PRD 15](15-data-model.md)).
2. **Runner** — `load_pack → run_one/run_all`, per-case timeout, error capture; a case failure never aborts
   the pack. Library-first (the predecessor harness runner design).
3. **Driver adapters** — how agentdrill delivers an attack: `subprocess`, `python`, `http`, and per-harness
   drivers (Claude Code, Cursor, …). Same invocation-payload / run-envelope contract as the predecessor harness.
4. **Target adapters** — how agentdrill talks to the deployed stack: `agentgate`, `agentkeys`,
   `agentseatbelt`/`agentkernel`, `policyweave-output`, `agenthalt`.
5. **Oracle engine** — deterministic oracles first, optional LLM judge for qualitative cases; three
   dimensions (`compatibility` / `enforcement` / `integrity`); honest outcome split
   (`blocked` / `missed` / `degraded`) (the predecessor harness scoring engine).
6. **Evidence reader** — pulls agentwatch records/events for the run and ties each result to evidence.
7. **Reporter + benchmark publisher** — machine-readable JSON + human-readable Markdown; the public
   per-release table (honest, includes misses).
8. **Kill-time probe** — drives agenthalt/agentkeys revoke and measures latency to actual cessation.
9. **CI surface** — structured exit codes, GitHub Actions / GitLab output, `$GITHUB_STEP_SUMMARY`.
10. **Importer** — promptfoo / garak / AgentDojo / PyRIT → attack packs (connector boundary; P1).
11. **Tagger** — MITRE ATLAS + OWASP mapping on every pack/attack (P1).
12. **Attack-chain orchestrator** — sequences single cases into multi-step documented chains (recon →
    injection → misuse → exfil → cover-up), carrying state between steps; a chain's result records
    **where the chain broke** (F18, F25).
13. **Mutation engine** — bounded synthetic variants of documented patterns (argument fuzzing, payload
    perturbation, paraphrase); deterministic and seed-pinned like everything else; **mutation only — no
    novel capability** (F17, R16).
14. **Coverage reconciler** — consumes the agentwatch inventory (tools, MCP servers, capabilities) and
    reports exercised vs. unexercised surfaces; `gap:unexplained` must be zero, same discipline as
    agentwatch (F26).
15. **Policy loop** — a confirmed miss emits an **advisory** rule suggestion + what-if replay against
    agentpolicy/policyweave; never auto-applied (F21).
16. **Trend store** — benchmark history + per-defense-class deltas across releases; the "what got worse"
    view (F23).
17. **Severity + compliance reporter** — findings carry severity; OWASP LLM/Agentic, MITRE ATLAS, NIST AI
    RMF, EU AI Act Art. 12 mappings; evidence exportable to agentcomply (F24).
18. **Trigger watcher (CART)** — subscribes to config/policy/model/harness-change events and re-runs the
    affected packs; drift alerts are triggers, not noise (F22).
19. **Evidence bundler** — per-finding shareable bundle (case + manifest + agentwatch refs), third-party
    verifiable offline (F27).
20. **Recon/scoping phase** — probes the target stack's exposed surface (via agentwatch inventory) and binds
    cases to what exists before running; missing surfaces fail loudly (F42).
21. **Kill-chain timer** — stage timestamps across the whole chain (attack-start → detected → decided →
    halted → revoked → ceased), published as a per-case timeline (F37).
22. **Attribution engine** — correlates a blocked→missed flip with the target-config diff, pin change, or
    adapter change that caused it; emits `attributed_to` on the finding (F38).
23. **Adaptive orchestrator (bounded)** — mutates documented patterns from live target responses,
    hard-capped inside the dual-use boundary, results labeled `adaptive` (F40).
24. **Meta-verification suite** — drill-the-drill adversarial cases against our own oracle engine, in CI
    beside the evasion pack (F43).
25. **HITL review queue** — local-first review queue for judge divergences; reviewed verdicts become seed
    corpus for future deterministic oracles (F44).
26. **Registry service (local-first + publishable index)** — pack signing, semver/changelog, deprecation,
    `pack publish/verify/deprecate` (F39).
27. **Fleet aggregator** — same pack across many stacks (opt-in, self-hosted), per-stack honest coverage
    rollups (F45).
28. **Authoring SDK** — `init` scaffolding, pytest-style case API, pack lint, fixture recording (F46).
29. **Notifier** — PR annotations + release-gate alerts naming case/stage/evidence/attribution (F47).

## The proof pipeline

| Stage | What happens | Inherited from |
|---|---|---|
| **Load** | Parse a versioned **attack pack** (YAML): cases = attack steps + the target they address + the oracle that decides blocked/missed/degraded. | the predecessor harness scenario pack |
| **Parameterize** | Bind the pack to a named target config (harness, stack endpoints, pinned model/seed). | the predecessor harness adapter contract + env labeling |
| **Attack** | Execute each case through a **driver adapter**; capture the attack trajectory (what was attempted). | the predecessor harness runner + trajectory capture |
| **Observe** | Read security events/records from agentwatch (`denied`, `policy-fired`, `revoked`, `halted`, `secret-detected`). | agentwatch security-event schema |
| **Decide** | Evaluate the **oracle**: `blocked` / `missed` / `degraded`; optional LLM judge for qualitative cases. | the predecessor harness deterministic + judge scoring |
| **Report** | Emit honest results + kill-time; machine- and human-readable; feed the public benchmark. | the predecessor harness reports + comparison |
| **Gate** | Exit non-zero when a case that must be blocked is not — the CI pass/fail gate on policy PRs. | the predecessor harness CI exit codes |

## Driver adapters (the invocation contract, absorbed)

agentdrill invokes a driver the way the predecessor harness invoked an agent — with **no ground-truth leakage**.

- **Invocation payload** sent to the driver contains only: `input`, `context`, `allowed_tools`,
  `disallowed_tools`, `budget`. The **oracle**, **expected outcome**, and thresholds **never** leave
  agentdrill (a drill you can read the answer to is not a drill).
- **Run envelope** the driver returns (JSON on stdout, logs on stderr):
  `{schema_version, status, output, trajectory, cost, error}`. Non-JSON stdout falls back to raw text with
  empty trajectory unless `strict_output=true`.
- **Adapters** (v0.1.0): `subprocess:./attack.py`, `python:pkg.mod:run`, `http://…/run`, plus **per-harness
  drivers** (`claude-code:…`, `cursor:…`) that deliver the attack through the harness's own surface.
- **Errors:** timeout → `status="timeout"`; crash/non-zero → `status="error"` with stderr; both continue
  the pack. Python callables run in a separate process for a hard timeout + isolation.

## Target adapters (the deployed stack)

Each target adapter knows how to (a) drive a component into an attack posture and (b) read back its
decision + evidence:

| Target | Driven to | Evidence read |
|---|---|---|
| `agentgate` | route a poisoned/shadowed MCP tool call | tool-call deny/allow + schema |
| `agentkeys` | request a brokered credential in an attack context | grant/deny, revocation |
| `agentseatbelt` / `agentkernel` | attempt confined action (write/exec/egress) | confinement verdict |
| `policyweave-output` | submit an action a compiled rule should stop | `policy-fired` / pass |
| `agenthalt` | trigger halt/revoke; measure cessation | `halted`, `revoked`, latency |

## Oracles & scoring

agentdrill reuses the predecessor's hybrid scoring engine, re-pointed:

- **Deterministic oracles first** (cheap, free, reproducible): did the stack block, deny, confine, or halt?
  Threshold-driven pass/warn/fail. The judge is **skipped** when a deterministic oracle cleanly decides.
- **LLM-as-judge** only for qualitative cases (e.g. refusal quality, explanation adequacy).
- **Hybrid** — the deterministic gate always runs, even with no judge configured, so enforcement checks are
  never silently skipped offline (`judge_not_evaluated: true`).
- **Evaluation hierarchy** → **enforcement > integrity > efficiency**: a missed attack (enforcement)
  trumps an incomplete evidence trail (integrity), which trumps a slow run (efficiency).
- **Three dimensions**, each independently gatable in CI:
  `compatibility` (target reachable, adapter healthy), `enforcement` (blocked vs missed),
  `integrity` (evidence present, kill-time measured, no hidden degradation).
- **Outcome split** (the honest label): `blocked` / `missed` / `degraded` (+ `blocked-below-threshold`).
- **Divergences:** deterministic pass ≠ judge pass → classified `critical` (wrong path, right-looking
  result) or `warning` (right path, poor answer) — gate with `--fail-on-divergence critical`.
- **Failure taxonomy:** `safety_miss`, `policy_miss`, `evidence_gap`, `kill_slow`, `target_error`,
  `pack_error`, `timeout`, `adapter_error`, `unknown` (from the predecessor's `FailureTaxonomy`).

## Two-layer defense (absorbed, reframed)

the predecessor's JPS study proved a deterministic evaluator and an LLM judge **fail differently and barely
overlap**. agentdrill keeps the same discipline:

1. **Deterministic oracles** catch structurally-decidable outcomes (was the call denied? did revocation
   stop the agent?) — the majority of a security drill.
2. **LLM judge** catches what rules can't express (was the refusal explanation adequate? did the agent
   look like it *tried* to comply?).
3. **Flag divergences** rather than averaging them away.

## Extensibility (plugin registry, absorbed)

- **Custom oracles** and **custom target/driver adapters** register via a decorator + entry points, and are
  validated at load (`unknown metric → ConfigError`).
- **Community packs** are executable security claims: reviewed like code (P1, R11), with a trust level
  (`built-in` / `local` / `external`) — the deferred-and-now-required trust model from the predecessor's security
  review.
