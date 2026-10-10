# ADR-0006 — Deterministic oracles first; judge only where needed

- **Status:** proposed
- **Context:** a security drill must be cheap, reproducible, and offline-capable; LLM judges are slow, costly,
  and non-deterministic.
- **Decision:** deterministic oracles run first and, on a clean decision, skip the judge; the judge runs only
  for qualitative cases; the hybrid gate **always** runs even offline (`judge_not_evaluated: true`) so
  enforcement checks are never silently skipped (DD-04, DD-07).
- **Consequences:** the majority of a drill is free and reproducible; divergences between the two layers are
  flagged, not averaged away.
