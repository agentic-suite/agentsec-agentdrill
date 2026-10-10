# ADR-0005 — Drivers never receive oracles/expected outcomes

- **Status:** proposed
- **Context:** a drill whose target can read the expected outcome measures nothing.
- **Decision:** the invocation payload sent to a driver contains only `input`, `context`, `allowed_tools`,
  `disallowed_tools`, `budget`; `oracle`/`expect`/thresholds stay inside agentdrill (DD-03). A guard test
  asserts this per driver.
- **Consequences:** attacks cannot be gamed by reading ground truth; the contract is enforceable. Adapters
  that accidentally forward the full pack fail the guard.
