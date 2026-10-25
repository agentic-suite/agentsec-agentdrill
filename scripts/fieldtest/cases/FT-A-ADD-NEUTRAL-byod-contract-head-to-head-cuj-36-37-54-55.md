# FT-A-ADD-NEUTRAL — BYOD contract + head-to-head (CUJ-36/37/54/55)

**Layer:** host · **LLM:** no · **Requires:** python · **PRD / claim:** PRD 29 CUJ-36/37/54/55 · **Suite:** track-a · **Class:** P/F

## Goal
BYOD contract + head-to-head (CUJ-36/37/54/55). See `docs/field-test/v0.1.0/field-test-plan.md` for the rationale.

## Steps
Run by `cases/steps/FT-A-ADD-NEUTRAL.sh` (generated from `gen_cases.py`); every command is
captured to `commands.log`.

## Assertions
The case-specific assertions in `cases/steps/FT-A-ADD-NEUTRAL.sh` (each recorded in
`assertions.ndjson`, with the command it ran and a **grounded** flag).
**Pass = every assertion true AND ≥1 grounded check** (`check_grounding.py`).

## LLM capture (must)
An LLM-required case records its request/response pair(s) under
`artifacts/llm/` (sanitized); a pass with no capture fails.

## Artifacts
`field-test/v0.1.0/results/<run-id>/cases/FT-A-ADD-NEUTRAL/artifacts/`.

## Cleanup
Shared stack: reset in place between cases; `recycle` cases get a fresh `down -v`
+ boot. The stack is torn down once, at the end of the run.
