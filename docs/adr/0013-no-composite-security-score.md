# ADR-0013 — No composite security score; per-finding CVSS v4.0 + AIVSS only

- **Status:** proposed (2026-10-10)
- **Context:** Buyers expect CVSS/AIVSS-style severity, but a single aggregate score can hide a critical
  miss behind an average (the PRD's anti-"security score" stance) and makes results gameable.
- **Decision:** Findings carry a **per-finding** severity = **CVSS v4.0 base + an OWASP AIVSS amplification
  vector** (autonomy, tools, language, context, non-determinism, opacity, persistence, identity, multi-agent,
  self-modification). Severity is **never aggregated** into a composite score or headline number. Results
  publish the honest outcome split (`blocked/missed/degraded`), tiers, CIs and misses
  ([PRD 42](../prd/42-standards-and-claims.md), [PRD 41](../prd/41-platform-compatibility.md)).
- **Consequences:** satisfies buyer expectation of a standard severity vector while preserving the
  no-scoring-theater principle; AIVSS is pre-1.0 → version-pin and re-score on change; reports must render
  vectors, not a single number.
