# Standalone Verifier

**Status:** design intent. An offline, zero-install verifier for agentdrill's published artifacts.

## What it is

Given a benchmark release or evidence bundle, `agentdrill verify <artifact>` — or the bundled verifier — runs
**offline** (no network, no drill install beyond the verifier) and returns three unambiguous verdicts:

| Verdict | Meaning |
|---|---|
| **intact** | signatures + hashes + manifest bindings check out |
| **complete** | every claimed case + evidence is present; gaps are flagged, not hidden |
| **honest-shaped** | labels (efficacy, attestation, severity) present; numbers multi-seed with CIs; redaction receipts verify |

On failure it names the **first broken link**.

## Why it matters

A reviewer, journalist, or auditor verifies our numbers **without trusting us and without re-running the
drill** — the same trust shape as agentwatch's evidence journey.

## Reference artifacts

- `SHA256SUMS` + signatures for the release.
- The redaction-receipt policy the verifier checks bundles against.

> The verifier proves **artifact integrity and honest shape**; it does not re-execute the drill. Reproduction
> is the separate runbook ([reproduce-the-benchmark](../../runbooks/reproduce-the-benchmark.md)).
