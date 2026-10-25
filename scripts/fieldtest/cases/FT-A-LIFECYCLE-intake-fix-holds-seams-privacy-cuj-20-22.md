# FT-A-LIFECYCLE — Intake, fix-holds, seams, privacy (CUJ-20..22)

**Layer:** host · **LLM:** no · **Requires:** python · **PRD / claim:** PRD 04 CUJ-20/21/22, PRD 20 · **Suite:** track-a · **Class:** P/F

## Goal
Intake, fix-holds, seams, privacy (CUJ-20..22). See `docs/field-test/v0.1.0/field-test-plan.md` for the rationale.

## Steps
Run by `cases/steps/FT-A-LIFECYCLE.sh` (generated from `gen_cases.py`); every command is
captured to `commands.log`.

## Assertions
The case-specific assertions in `cases/steps/FT-A-LIFECYCLE.sh` (each recorded in
`assertions.ndjson`, with the command it ran and a **grounded** flag).
**Pass = every assertion true AND ≥1 grounded check** (`check_grounding.py`).

## LLM capture (must)
An LLM-required case records its request/response pair(s) under
`artifacts/llm/` (sanitized); a pass with no capture fails.

## Artifacts
`field-test/v0.1.0/results/<run-id>/cases/FT-A-LIFECYCLE/artifacts/`.

## Cleanup
Shared stack: reset in place between cases; `recycle` cases get a fresh `down -v`
+ boot. The stack is torn down once, at the end of the run.
