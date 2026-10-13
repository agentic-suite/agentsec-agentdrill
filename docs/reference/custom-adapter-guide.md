# Custom Adapter Guide

**Status:** normative (M4). API: [adapter-api.md](adapter-api.md) · Design:
[../design/adapter-contract.md](../design/adapter-contract.md).

An **adapter** is how an attack reaches a harness. Implement the `Driver` ABC, register it, and reference it
from a case's `driver.type`.

## 1. Implement the driver

```python
from typing import Any
from agentdrill.drivers import Driver

class MyDriver(Driver):
    """Deliver the attack through my harness."""
    name = "my-harness"

    def _invoke(self, payload: dict[str, Any], config: dict[str, Any]) -> Any:
        # payload is the restricted attack payload (no ground truth).
        # Return a run envelope dict (see schema/run-envelope.schema.json) or raw text.
        return {
            "schema_version": "agentdrill.run_envelope.v1",
            "status": "completed",
            "output": {"final": "…", "structured": None},
            "trajectory": {"steps": [{"type": "tool_call", "tool": "shell"}]},
            "cost": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "cost_usd": 0.0},
        }
```

Rules:

- **Never receive ground truth.** `build_payload` gives you only `case_id`, `goal`, `target`, `attack`
  (steps) and `budget`. Do not read `case.oracle`.
- **Raise, don't lie.** `AgentTimeoutError` on timeout, `AdapterError` on any other failure — the runner maps
  these to `status`.
- **Return the envelope or raw text.** A `str` is treated as raw stdout (text output, empty trajectory).

## 2. Register it

Programmatically:

```python
from agentdrill.drivers.registry import register, manifest_for
register(MyDriver)
manifest = manifest_for(MyDriver)  # name + SHA-256 digest
```

Or ship it as an entry point so `discover()` finds it:

```toml
# pyproject.toml of your package
[project.entry-points."agentdrill.drivers"]
my-harness = "my_pkg.driver:MyDriver"
```

Unknown / unregistered names fail loudly with `ConfigError` — never a silent no-op.

## 3. Use it from a pack

```yaml
cases:
  - id: my-case
    driver: {type: my-harness, config: {…}}
```

Run it:

```python
from agentdrill.attack_runner import AttackRunner
from agentdrill.drivers.registry import get_driver, manifest_for

driver = get_driver("my-harness")
AttackRunner(driver, driver_manifest=manifest_for(type(driver)).to_dict()).run_all(pack)
```

## Guarantees

- **No ground-truth leakage** — asserted per driver.
- **Digest-bound** — the adapter manifest's SHA-256 digest is written into `run.json`.
- **Never silent** — unknown names and unreachable surfaces fail before any case runs.
