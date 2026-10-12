# Pack Format — Specification

**Status:** **normative** for the pack schema, loader, resolution and hashing (implemented M2); the
remaining runtime semantics (drivers, oracles, evidence) are design intent until their milestones land.
Design: [../design/pack-format.md](../design/pack-format.md). Loader: `src/agentdrill/loading/attack_pack_loader.py`.

## Top-level

```yaml
pack:
  name: <string>            # required
  version: <semver>         # required
  description: <string>     # required
  min_agentdrill: <semver>  # required
  license: <spdx>           # required
  trust: built-in|local|external   # required
cases: [<case>, ...]        # required, non-empty
```

## Case

```yaml
- id: <^[a-zA-Z0-9_-]+$>     # required, path-safe
  title: <string>           # required
  goal: <string>            # required
  incident_ref: <string>    # required
  target: {type: <target>, config: {…}}   # required
  driver: {type: <driver>, config: {…}}   # required
  attack: {steps: [{tool: <string>, args: {…}}]}   # required
  benign_twin: <case-id>    # required for enforcement cases
  oracle:
    expect: blocked|missed|degraded   # required
    dimensions: [compatibility|enforcement|integrity]
    expect_telemetry: [<event>, ...]
    kill_time: {max_seconds: <int>}
  cleanup: [{cmd: <string>, expect: success}]     # required for stateful cases
  tags: [<tag>, ...]        # required (must include ATLAS + OWASP)
  difficulty: easy|medium|hard
  budget: {max_steps: <int>, max_cost_usd: <float>}
```

## Validation rules

1. `pack.*` required fields present; semver parseable.
2. `trust` ∈ {built-in, local, external}; external ⇒ sandbox-only (only a sandbox driver is accepted).
3. Case `id` unique within pack; matches `^[a-zA-Z0-9_-]+$` **before any path use**.
4. `target.type` / `driver.type` / oracle vocabulary resolve in the registry — unknown ⇒ `ConfigError` (exit 2).
   The registry is the single source of truth (`src/agentdrill/loading/attack_registry.py`).
5. `oracle.expect` ∈ {blocked, missed, degraded}; `dimensions` ⊆ the three; `expect_telemetry` ⊆ the
   agentwatch security-event vocabulary (`denied`, `policy-fired`, `secret-detected`, `revoked`, `halted`).
6. Enforcement cases should declare `benign_twin`; a declared `benign_twin` must reference a case in the pack.
   (Presence enforcement is owned by the efficacy control, M13.)
7. `tags` non-empty and include at least one ATLAS and one OWASP tag (catalog lint).
8. Budgets coherent (non-negative, within platform maxima).
9. Errors carry a location (file + line) and never silently pass.

`min_agentdrill` gates compatibility: a pack that requires a newer agentdrill than the running one fails at
load (loud).

## Hashing

The pack content hashes to SHA-256 at load and is set on `pack.hash`; results bind to `pack@version+hash`
(helper `pack_ref`) — golden-lock, DD-28. A changed pack ⇒ a new hash ⇒ a changed number must be re-published
with a note.
