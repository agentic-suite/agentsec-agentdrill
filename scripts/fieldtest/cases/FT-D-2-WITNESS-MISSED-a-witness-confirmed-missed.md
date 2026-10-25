# FT-D-2-WITNESS-MISSED — A witness-confirmed missed

**Layer:** host · **LLM:** no · **Requires:** python · **PRD / claim:** WBS part 17 SS4.4.2 · **Suite:** demos · **Class:** P/F

## Goal
A witness-confirmed missed. See `docs/field-test/v0.1.0/field-test-plan.md` for the rationale.

## Steps
Run by `cases/steps/FT-D-2-WITNESS-MISSED.sh` (generated from `gen_cases.py`); every command is
captured to `commands.log`.

## Assertions
The case-specific assertions in `cases/steps/FT-D-2-WITNESS-MISSED.sh` (each recorded in
`assertions.ndjson`, with the command it ran and a **grounded** flag).
**Pass = every assertion true AND ≥1 grounded check** (`check_grounding.py`).

## LLM capture (must)
An LLM-required case records its request/response pair(s) under
`artifacts/llm/` (sanitized); a pass with no capture fails.

## Artifacts
`field-test/v0.1.0/results/<run-id>/cases/FT-D-2-WITNESS-MISSED/artifacts/`.

## Cleanup
Shared stack: reset in place between cases; `recycle` cases get a fresh `down -v`
+ boot. The stack is torn down once, at the end of the run.
