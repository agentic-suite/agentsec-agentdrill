# ADR-0008 — Kill-time is a cessation probe, not an event receipt

- **Status:** proposed
- **Context:** revocation that *reports* success while the agent keeps acting is the worst failure mode —
  the dashboard is green and the damage continues.
- **Decision:** measure the full kill chain (attack_start → delivered → detected → decided → halted →
  revoked → **ceased**), and establish `ceased` by **re-attempting the guarded action** post-revoke, not by
  an event receipt (R8). Report per-stage p50/p95/max; a `cease_gap` (revoked but still acting) is the
  highest-severity finding.
- **Consequences:** the measured end is real cessation; a missing stage is flagged, never inferred.
