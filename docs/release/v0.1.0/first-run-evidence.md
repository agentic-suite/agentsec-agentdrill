# First-Run Evidence — v0.1.0

**Status:** ✅ **recorded** 2026-10-25 (WBS M32, work item 32.2).

## Target

Fresh machine → first honest drill result in **≤15 minutes**, zero code changes, against the bundled demo
stack.

## Evidence

| Item | Value |
|---|---|
| Machine | fresh container from `agentdrill-fieldtest:local` (Linux/aarch64, Python 3.11.17) — no prior state |
| Install command | `pip install agentsec-agentdrill` (the image ships it; this is the clean baseline) |
| First-run command | `agentdrill quickstart` |
| Time to first result | **0.70 s** internal (**~2 s** wall) against a **≤15 min** budget — pass, large margin |
| Outcome | demo-watermarked `never evidence`: `outcome: blocked 3, missed 2, degraded 0` (includes a deliberate miss) |
| Attestation | `mock` — the demo is **non-evidence**; a mock attestation is refused by a real consumer |
| Preflight | `agentdrill doctor` → **OK** (Python 3.11.17, version 0.1.0, 8 adapters, output dir writable) |

Reproduce:

```sh
docker run --rm agentdrill-fieldtest:local agentdrill doctor
docker run --rm agentdrill-fieldtest:local agentdrill quickstart
```

## Also recorded

- The **live** first run against a real stack (attestation `live`) is the field test's Track A runs —
  [FIELD_TEST_REPORT.md](../../field-test/v0.1.0/FIELD_TEST_REPORT.md), `FT-A-QUICKSTART` and the core CUJ
  suites.
- The demo evidence bundle opens **offline** with `agentdrill verify` ([verifier](../verifier/README.md)).

## Guard

`tests/test_m32_first_run.py` runs the container quickstart and asserts it returns the expected
outcome within the 15-minute budget.
