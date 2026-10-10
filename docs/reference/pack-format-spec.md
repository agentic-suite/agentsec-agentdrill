# Pack Format — Specification

**Status:** draft (design intent). Normative once implemented. Design: [../design/pack-format.md](../design/pack-format.md).

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
2. `trust` ∈ {built-in, local, external}; external ⇒ sandbox-only (`config` cannot name a non-subprocess driver).
3. Case `id` unique within pack; matches `^[a-zA-Z0-9_-]+$` **before any path use**.
4. `target.type` / `driver.type` resolve in the registry — unknown ⇒ `ConfigError` (exit 2).
5. `oracle.expect` ∈ {blocked, missed, degraded}; `dimensions` ⊆ the three; `expect_telemetry` ⊆ agentwatch events.
6. Enforcement cases require `benign_twin`; stateful cases require `cleanup`.
7. `tags` non-empty and include at least one ATLAS and one OWASP tag.
8. Budgets coherent (non-negative, within platform maxima).
9. Errors carry a location (file + line) and never silently pass.

## Hashing

The pack content hashes to SHA-256; results bind to `pack@version+hash`. A changed pack ⇒ a new hash ⇒ a
changed number must be re-published with a note (golden-lock, DD-28).
