# FT-B-OA-AZURE — Agent matrix: oa-azure (openai-agents)

**Layer:** host · **LLM:** yes · **Requires:** docker,llm · **PRD / claim:** PRD 04 Track B, plan SS4.2 · **Suite:** track-b · **Class:** P/F

## Goal
Agent matrix: oa-azure (openai-agents). See `docs/field-test/v0.1.0/field-test-plan.md` for the rationale.

## Steps
Run by `cases/steps/FT-B-OA-AZURE.sh` (generated from `gen_cases.py`); every command is
captured to `commands.log`.

## Assertions
The case-specific assertions in `cases/steps/FT-B-OA-AZURE.sh` (each recorded in
`assertions.ndjson`, with the command it ran and a **grounded** flag).
**Pass = every assertion true AND ≥1 grounded check** (`check_grounding.py`).

## LLM capture (must)
An LLM-required case records its request/response pair(s) under
`artifacts/llm/` (sanitized); a pass with no capture fails.

## Artifacts
`field-test/v0.1.0/results/<run-id>/cases/FT-B-OA-AZURE/artifacts/`.

## Cleanup
Shared stack: reset in place between cases; `recycle` cases get a fresh `down -v`
+ boot. The stack is torn down once, at the end of the run.
