# ADR-0007 — Unguarded control group (efficacy) is mandatory

- **Status:** accepted
- **Context:** a `blocked` number means nothing unless the attack demonstrably succeeds against an
  *unguarded* stack; without a control group the benchmark measures nothing (the SWE-Bench flawed-tests
  lesson).
- **Decision:** every case runs against an **unguarded twin**; only **efficacy-verified** cases count
  (F59). An attack that fails unguarded is `attack_inert` — flagged and **excluded** from enforcement rates,
  never used to pad a green table.
- **Consequences:** every published number is backed by a case proven to land; an inert case cannot inflate
  coverage. Efficacy re-verifies on pack release and on target change.
