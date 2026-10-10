# OpenSSF Best Practices

agentdrill targets the **OpenSSF Best Practices** baseline (passing), with the org governance floor applied.
Design intent; the badge is recorded at release readiness (M24).

## Baseline artifacts

| Criterion area | agentdrill evidence |
|---|---|
| Security policy | [SECURITY.md](../../SECURITY.md) + org policy |
| Supply chain | SBOM (CycloneDX), signed artifacts + provenance (Sigstore), DCO, dependency review |
| Secure development | deterministic quality gate (`ruff`, `mypy --strict`, coverage ≥95%), code review (PR + CODEOWNERS) |
| Threat model | [../design/threat-model.md](../design/threat-model.md) |
| Assurance case | test strategy ([../plans/testing-and-parity-strategy.md](../plans/testing-and-parity-strategy.md)) + meta-verification + evasion pack |
| Vulnerability reporting | private disclosure process; advisories via org |

## Agentic-specific posture

- **Self-attack as a control:** the evasion pack (R7) continuously red-teams the ecosystem's own tools.
- **Honest efficacy:** unguarded control group (ADR-0007); published misses.
- **Signed, verifiable results:** Sigstore + an offline verifier.

The OpenSSF Scorecard grade is recorded in the release evidence at M24.
