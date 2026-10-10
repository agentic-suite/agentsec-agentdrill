# Tutorial 03 — Run in CI

**You'll get:** a workflow that rejects a policy change that un-blocks a known attack.

## GitHub Actions

```yaml
name: drill
on: [pull_request]
jobs:
  drill:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install agentsec-agentdrill
      - run: agentdrill validate --pack incidents-core --strict
      - run: |
          agentdrill run \
            --pack incidents-core \
            --target ./stack.yaml \
            --ci --fail-on enforcement --output-format github-actions
```

## What the gate does

- A must-block case that returns `missed` → non-zero exit (**1**, or **4** for a critical enforcement miss).
- The PR is annotated with the **case**, the **stage**, the **evidence ref**, and **attribution**.
- `--fail-on compatibility|enforcement|integrity` gates each dimension independently.
- `--fail-on-divergence critical` forks a deterministic-vs-judge divergence.

## Fast path vs full

- **Per commit:** deterministic oracles + fixtures (no API keys) — the smoke subset.
- **Nightly / pre-release:** full pack + judge.

## Change-driven

- A config/policy/model/harness change triggers only the **affected** packs (trigger watcher, F22).
- Out-of-PR drift (vendor model update, MCP rug-pull) is caught by `agentdrill schedule` (F71).

## Next

- Prove the kill chain → [04 — Verify kill-time](04-verify-kill-time.md)
