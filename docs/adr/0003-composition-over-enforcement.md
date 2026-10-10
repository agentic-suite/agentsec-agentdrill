# ADR-0003 — agentdrill owns no enforcement

- **Status:** proposed
- **Context:** a drill that enforces would be testing itself, not the user's stack.
- **Decision:** agentdrill **drives** the deployed enforcement path (agentgate, agentkeys,
  agentseatbelt/agentkernel, policyweave output, agenthalt) and **reads** evidence (agentwatch); it never
  becomes a control (DD-01, DD-02).
- **Consequences:** the runner is thin; the enforcement stays in the enforcers; results reflect the real
  stack. Scope creep into enforcement is a review-blocking violation ([PRD 14](../prd/14-non-goals.md)).
