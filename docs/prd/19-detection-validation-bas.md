# PRD 19 — Detection Validation & BAS-Class Features

**BLUF:** The classic red-team ecosystem (Caldera, Atomic Red Team, BAS vendors) solved problems LLM
tooling rediscovered: **every attack test must clean up after itself, validate the telemetry actually
fired, report utility cost, and render as a coverage heat-map.** agentdrill absorbs those patterns:
per-case cleanup, expected-telemetry validation, utility-under-attack reporting, bootstrap confidence
intervals, adversary profiles, plugin discovery, per-row traces, PR-based submissions, and multi-format
operation reports.

**Status:** Draft — v0.1.0 (2026-10-09) · **Owner:** @deghosal-2026 · **Parent:** agentic-suite #209 · Features: F49–F58

## What the classic tools got right

| Source tool | Pattern | agentdrill feature |
|---|---|---|
| **MITRE Caldera** | adversary profiles, chained procedures, cleanup functions, operation reports (JSON/CSV/PDF) | F55, F16 (chains), F54, F58 |
| **Atomic Red Team** | portable YAML atomics, `get_prereqs`, cleanup commands, executor-agnostic | F42 (recon/prereqs), F54, F16 |
| **garak (NVIDIA)** | plugin architecture (`--list_probes/--list_detectors/--list_generators`), HTML hitlog, **bootstrap confidence intervals on ASR** (v0.14.1) | F49, F50, F53 |
| **AgentDojo** | **utility vs utility-under-attack vs targeted-ASR** (three-metric frame), traces published per leaderboard row, **PR-based results submission** | F51, F56, F57 |
| **BAS vendors** (Safe/Scythe/Cymulate) | **expected-telemetry validation** (did the SIEM actually alert?), coverage heat-maps per control | F52, F53 |

## F49 — Plugin discovery & introspection

garak's `--list_probes` pattern, applied to every agentdrill extension point:

```sh
agentdrill list packs      # installed packs, versions, trust levels, tags
agentdrill list oracles     # registered oracles (deterministic | judge | hybrid)
agentdrill list targets     # target adapters + recon requirements
agentdrill list drivers     # driver adapters + config keys
agentdrill plugin info <name>   # garak-style: description, default params, required secrets (names only)
```

Unknown names fail loudly at load (`ConfigError`, exit 2) — same discipline as the oracle registry
(PRD 02).

## F50 — Per-case cleanup & dirty-target detection

Caldera/ART's non-negotiable: an attack test that mutates target state and doesn't restore it invalidates
every subsequent case.

```yaml
cleanup:
  - {cmd: "restore-compiled-policy", expect: success}
  - {cmd: "agentkeys restore revoked-credential <ref>"}
```

- Cleanup runs **after every case**, even failed/timeout ones.
- **A cleanup failure is a release-blocking finding** (`dirty_target`), not a warning: a dirty target
  makes every later number untrustworthy.
- Cleanup steps are timed and recorded in the evidence bundle (what was restored, when, verified how).

## F51 — Utility-under-attack reporting (the AgentDojo three-metric frame)

AgentDojo's core insight: a defense that blocks attacks but destroys benign utility is a bad defense
(prompt sandwiching: ASR improves, utility stays broken). Every published pack result carries all three:

| Metric | Meaning |
|---|---|
| **benign utility** | Does the stack pass the agent's *benign* twin cases (same tools, no attack)? |
| **utility under attack** | Benign utility *while* the pack's attacks are in play |
| **enforcement rate** | blocked / (blocked + missed) |

- Every attack case has an optional `benign_twin:` case id; the pair runs together.
- A defense with high enforcement + collapsed utility-under-attack gets a `utility_cost` finding —
  **agentdrill never lets a "100% blocked" number stand without its utility price tag.**

## F52 — Expected-telemetry validation (did the control actually *say* so?)

The BAS pattern, applied to agentwatch: each case declares which security events *should* fire when the
defense works:

```yaml
oracle:
  expect: blocked
  expect_telemetry: [policy-fired, halted]   # agentwatch events that must accompany a true block
```

- A `blocked` verdict with **no corresponding agentwatch event** = `telemetry_gap` finding — the control
  blocked the attack but its evidence path is broken (dashboards/alerts/agentcomply will be blind to the
  next one).
- This closes the loop agentwatch opened (`gap:unexplained = 0`): the drill now also proves the
  *observability* of the defense, not just its behavior.

## F53 — Coverage heat-map & posture scorecard

The most recognizable red-team artifact (AT&CK-navigator/BAS style), rendered per release:

- **Matrix:** pack (or ATLAS/OWASP tag) × deployed control → cell = `blocked | partial | missed |
  untested`.
- `partial` = blocked the chain but past the stage where it *should* have broken (ties into F37).
- Published per release as part of the benchmark; the **delta between release heat-maps is the trend
  store's (F23) visual form**.

## F54 — Adversary profiles (pack-level threat-intel cards)

Caldera adversary profiles: every pack carries a card — *who we're emulating, what they did, source
citation, objective* — so a pack reads as threat intel, not a test list. `incident_ref` (PRD 15) is the
machine field; the profile is the human one.

## F55 — Bootstrap confidence intervals on outcome rates

Beyond mean ± std (F29): blocked/missed rates across seeds get **bootstrap CIs**, the garak v0.14.1
pattern — non-normal outcome distributions (rates near 0/1) get honest intervals. Published tables show
`blocked 87% [81%, 92%] (n=150, 5 seeds)`, never a bare percentage.

## F56 — Traces with every published row

AgentDojo's leaderboard discipline: every published benchmark row links its **full attack trajectory +
evidence refs**. No aggregate number without its underlying traces — a reviewer can drill from the table
cell to the exact run, in one hop.

## F57 — PR-based benchmark submission (external tools, R12 enabler)

AgentDojo's "fork → run → PR with results" flow, for external defenses submitting to our benchmark:

1. Fork the benchmark repo, run your stack against the pinned pack set.
2. Open a PR with your results (manifest + traces), produced by `agentdrill benchmark export`.
3. Review: reproduction check (CUJ-3) → merge into the published table with your attribution.

This is the convention-winning mechanic (PRD 07): we don't need vendors to *agree* to be benchmarked —
the benchmark is reproducible enough that anyone can submit.

## F58 — Multi-format operation reports

Caldera pattern: every run emits JSON (machine), Markdown (PRs), and a self-contained **HTML operation
report** (exec-shareable, offline-openable — same constraints as agentwatch's demo bundle). PDF where
compliance consumers need it (agentcomply may re-render).

## Traceability additions

| Req | Feature | Test |
|---|---|---|
| R26 Cleanup discipline | F50 | A case with failing cleanup blocks release (`dirty_target`) |
| R27 Utility cost | F51 | A blocked verdict without a benign-twin utility number fails publish |
| R28 Telemetry validation | F52 | `blocked` + no expected agentwatch event ⇒ `telemetry_gap` finding |
| R29 Bootstrap CIs | F55 | Publish check: bare percentages rejected |
| R30 Traces per row | F56 | Every benchmark cell links a trajectory + manifest |
| R31 PR submission | F57 | An external submission reproduces via CUJ-3 path |
| R32 Heat-map | F53 | Per-release heat-map + delta generated in CI |

## What this is not

- Not a full Caldera/ART replacement — those emulate *network* adversaries; agentdrill replays *agent*
  incidents. The patterns transfer; the domains don't overlap.
- Not vendor telemetry ingestion — expected-telemetry validation reads **agentwatch** only (one schema,
  one source of truth).