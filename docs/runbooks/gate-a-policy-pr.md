# Runbook — Gate a Policy PR

**Goal:** a policy change that un-blocks a known attack is **rejected before merge**.

```sh
# In CI, against the candidate stack
agentdrill run --pack incidents-core \
  --target ./candidate-stack.yaml \
  --ci --fail-on enforcement --output-format github-actions
```

**What happens**

1. The packs run against the candidate compiled policy.
2. A case that must be `blocked` returns `missed` → exit code **1** (or **4** for a critical enforcement case).
3. The PR annotation names the **case**, the **stage** where the chain broke, the **evidence ref**, and the
   **attribution** (`attributed_to`).

**On failure**

- Read the annotation → open the cited evidence (`agentdrill verify <bundle>` if handed one).
- Fix the rule; re-run.
- The confirmed miss becomes a **permanent regression case** bound to the fix (F61) — the fix is done when
  it *holds*, not when it ships.

**Guardrail:** the gate is itself drilled — a meta-verification case asserts a must-block miss exits
non-zero, so a silent pass-everything gate is caught ([design/ci-gate](../design/ci-gate.md)).
