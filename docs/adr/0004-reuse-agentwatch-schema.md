# ADR-0004 — Reuse the agentwatch record + security-event schema

- **Status:** proposed
- **Context:** the ecosystem already defines one record + security-event schema; drills produce
  machine-consumed results that must interoperate.
- **Decision:** agentdrill **consumes** the agentwatch schema (`denied`, `policy-fired`, `secret-detected`,
  `revoked`, `halted`) — never forks it (DD-05).
- **Consequences:** one source of truth; drills flow into analytics/compliance; a schema change is tracked,
  not silently absorbed.
