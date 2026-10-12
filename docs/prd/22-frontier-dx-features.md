# PRD 22 — Frontier & Developer-Experience Features

**BLUF:** The proof engine works when it disappears into the developer's loop. This PRD adds the DX and
frontier surfaces: **pack selection/diffing**, **watch mode**, **dry-run/explain**, **templates**,
**scheduled drills**, **CI-matrix export**, **programmatic assertions**, **provenance cards**, **registry
sync**, **diff-aware re-runs**, a **read-only MCP drill surface**, and **kill-time budgets as versioned
policy** — plus the frontier pack classes the incident register will demand next.

**Status:** Draft — v0.1.0 (2026-10-09) · **Owner:** @deghosal-2026 · **Parent:** agentic-suite #209 · Features: F67–F78

## Developer experience (the loop features)

### F67 — Pack diffing & selection
- `agentdrill pack diff <a> <b>` — case-level + coverage-tag delta between two pack versions; answers "what did upgrading this pack change about what we test?"
- `agentdrill list cases --tag <t> --target <x> --difficulty <d>` — targeted selection so a stack owner can run *their* surface without the whole catalog. Selection composes with `--dry-run` (F69).

### F68 — Watch mode
- `agentdrill watch` — local loop that re-runs **affected** packs on target-config/harness/policy file change. The interactive complement to the CI-side trigger watcher (F22): developers see a drill outcome on save, the same way they see tests on save. Uses the same recon→bind→affect computation as diff-aware re-runs (F76).

### F69 — Dry-run & explain plan
- `agentdrill run --dry-run` — prints the bound cases, their targets (attested, F63), expected oracle verdicts, and expected agentwatch telemetry (F52) **without executing**. The "what will happen" contract before anything fires.
- `--explain` — annotates *why each case exists* (incident_ref, adversary profile, the defense it probes). A reviewer of a policy PR sees the drill plan in the PR, not just the outcome.

### F70 — Pack template library
- `agentdrill init --template <class>` — scaffolds a pack from a documented incident class: `mcp-poisoning`, `exfil-chain`, `destructive-command`, `supply-chain`, `ssrf`, `sandbox-escape`, `memory-abuse`. Each template ships with oracle stubs, benign twins, cleanup, and the ATLAS/OWASP tag set pre-filled. The fastest path from "new incident" → "efficacy-verified pack" (CUJ-20's 7-day SLA depends on this).

### F71 — Scheduled drills (cron-mode)
- `agentdrill schedule` — pack sets on a cadence, findings filed as issues/PRs. Explicitly for attack surfaces that change **outside** the code-PR flow: vendor model updates, MCP server-side drift (rug-pulls), marketplace skill changes. CI triggers can't see those; a cadence can. Results land in the trend store (F23) with the trigger labeled `scheduled`.

### F72 — CI-matrix export
- `agentdrill export ci --format github-actions|gitlab` — one command emits the pack set + manifest + attestation as a CI matrix config. Adding a new deployed stack is "add one row," and its per-stack results flow into fleet rollups (F45) by construction.

### F73 — Programmatic assertions
```python
from agentdrill import Drill
d = Drill(pack="incidents-core@1.3.0", target="./stack.yaml")
r = d.run()
assert r.case("replit-destructive-command").blocked
assert r.case("exfil-01").kill_time.p95 < 5.0
```
- Teams embedding drills in their own test suites get pytest-native assertions over the same run objects the CLI produces — one engine, every surface (the same principle as the predecessor's lib-first design).

### F74 — Pack provenance cards
- Machine-readable card per pack: sources, dates, mutation policy, author, reviewers, efficacy status. Rendered on **every result** — a table cell traces to *people and reviews*, not just a commit hash. This is the model-card discipline applied to attack packs.

### F75 — Public registry sync
- `agentdrill registry sync` — read-only fetch of the signed public pack index (F39) so a fresh install pulls the ecosystem pack set without vendoring; signature-verified at sync. Consumers pin pack versions like dependency versions; `agentdrill pack outdated` reports drift against the index.

### F76 — Diff-aware re-runs
- When a target changes, only cases **bound to the changed surface** re-run — the recon snapshot (F42) and `attributed_to` (F38) drive selection. CI time scales with diff size, not catalog size. Full runs remain available (`--full`) and ship on release.

### F77 — MCP drill surface
- A **read-only MCP server** exposing pack/run/result queries ("what regressed?", "show me the misses for agentgate this release") so coding agents can consult the drill record mid-session without leaving the loop — the same posture as agentwatch's read-only MCP pattern. No write tools; queries themselves recorded as drill-record accesses.

### F78 — Kill-time budgets in policy
- Per-case `max_seconds` budgets published **inside policyweave output** alongside the enforcement rules — the budget is versioned, gated, and drilled exactly like the rule it accompanies. A latency regression becomes visible *in the same PR* as the rule change that caused it, not in a later benchmark.

## Frontier pack classes (in-scope v0.1.0, feeding the intake pipeline)

| Pack class | Cases from | Lands |
|---|---|---|
| **Rug-pull watch** | Server-side swap detection: same tool name, changed schema/description; shadow-tool hijack of trusted names | v0.1.0 (with MCP pack) |
| **Skill/capability content-swap** | Same version, changed content (Plugin4Shell class applied to skills/plugins/hooks/rules) | v0.1.0 |
| **Model-update drift** | Vendor model/silently-updated-model behavior change vs the pinned pack expectation — re-pin cadence cases | v0.1.0 |
| **Cross-tenant / context bleed** | Memory/state isolation across tasks, tenants, sessions (F20 depth) | v0.1.0 |
| **Denial-of-service budgets** | Agent loop/budget exhaustion as an attack (cost-amplification chains) | v0.1.0 |
| **CI runner abuse** | Untrusted repo content hijacking agents in CI (PR-triggered injection, workflow poisoning) | v0.1.0 |
| **A2A delegation abuse** | Cross-org agent-to-agent delegation, signed-card forgery | v0.1.0 (spec-stabilization-gated) |

## Traceability additions

| Req | Feature | Test |
|---|---|---|
| R41 Pack selection/diff | F67 | `pack diff` output matches case-delta fixture |
| R42 Local loop | F68 | Watch re-runs affected within 1 save; unaffected untouched |
| R43 Dry-run honesty | F69 | Dry-run performs zero driver executions (probe-verified) |
| R44 Templates | F70 | Template scaffold passes lint + efficacy review untouched |
| R45 Cadence | F71 | Scheduled finding lands as issue with trigger label |
| R46 CI export | F72 | Emitted matrix passes CI dry-run |
| R47 Embedding | F73 | Assertions green/red against fixture run objects |
| R48 Provenance | F74 | Card renders on result; reviewer fields non-empty |
| R49 Registry sync | F75 | Signature failure rejects index |
| R50 Diff-aware | F76 | Changed-surface case set = bound set, verified vs full run |
| R51 MCP surface | F77 | Read-only (no write tools present in tool list) |
| R52 Budget versioning | F78 | Budget change appears in same PR/diff as rule change |

## Sequencing

- All features F67-F78 land in **v0.1.0** (this release); frontier pack classes ship as intake delivers them (7-day SLA, CUJ-20)