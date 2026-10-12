# PRD 13 — Non-Functional Requirements

**BLUF:** agentdrill's non-functionals are dominated by **determinism** (reproducibility is the success
bar) and **honesty** (misses are first-class). It must be **portable** (harness-agnostic, local-first),
**safe to run untrusted packs**, and cheap enough to gate every policy PR.

**Status:** Draft — v0.1.0 (2026-10-09) · **Owner:** @deghosal-2026 · **Parent:** agentic-suite #209

## Determinism & reproducibility (primary)

- **Pinned inputs:** pack version + SHA-256 hash, pinned model(s), pinned seeds, pinned stack component
  versions.
- **Run manifest** (`run-manifest.json`) per run: OS, arch, runtime + version, dependency tree, target/driver
  digests, pack hash, environment **names** (never values). `--no-manifest` for privacy-sensitive runs.
- **Fixtures / ToolStub:** record-and-replay tool/stack responses so two identical fixture runs produce
  identical scores; `--live` for real execution (mutually exclusive with fixtures).
- **Documented methodology:** how each oracle decides `blocked`/`missed`/`degraded` is published; no
  proprietary scoring.
- **Same environment ⇒ same result** is a hard acceptance criterion (R6), verified by an automated
  reproducibility test (rerun ⇒ identical result unless a pin changed, which must be declared).

## Statistical trustworthiness (the benchmark-trust layer)

The 2026 benchmark-trust literature is brutal: contamination inflates scores, single-run claims mislead,
and silent updates destroy credibility (SWE-Bench Verified stopped reporting scores over contamination).
agentdrill treats those as **product requirements**, not caveats:

- **Multi-seed discipline (F29):** every published number is the mean ± standard deviation across
  **≥3 pinned seeds** — a single run is never a claim. Judge-based outcomes report confidence intervals.
- **Contamination checks (F30):** before a case's result is published, its content is checked for overlap
  with the judge/target model's training corpus posture (via probe queries); contaminated cases are
  **flagged in the table**, never silently dropped or kept.
- **Preregistration (F31):** expected outcomes per pack version are preregistered and locked; a result that
  differs from its golden is *flagged as a change*, never silently corrected.
- **Dark holdout (F33):** each pack keeps an unpublished holdout subset that runs in CI; published-set-only
  green + holdout red = pack-gaming, escalated as a finding.
- **Percentiles, not just means (F29):** kill-time latency reports p50/p95/max over repeated trials —
  "the mean is 3s" hides the 30s tail that actually kills you.
- **Adversarial adjudication (F32):** pack validation includes independent-reviewer cases (the JPS pattern
  that caught what author-written tests missed); published findings carry a public dispute process with a
  resolution SLA.
- **Limitations register (F34):** each release ships the honest "what this does NOT test" list.
- **Signed provenance (F35):** published packs/manifests/results are signed (Sigstore) with full provenance;
  authenticity is verifiable without re-running.

## Honesty (primary)

- A run **cannot** publish without its misses (R5).
- No composite "security score" that can hide a miss in an average.
- Every published number links its `run-manifest.json` + pack hash.

## Performance

- A single pack run completes locally in minutes; the CI smoke subset (deterministic oracles only, fixtures
  mode, no judge) gates per-commit cheaply.
- Parallel execution (`--workers`, `--max-outstanding`) with backpressure for large packs.
- Per-case timeout with hard process isolation (absorbed: python callables run in a separate process).
- Oracle/judge cache (TTL) to dedupe repeated judge calls; `cache stats` reports savings.

## Reliability & failure modes

- **A case failure never aborts the pack** (absorbed from the predecessor harness): timeout/crash/adapter error
  mark the case and continue; the run still reports.
- **Fail-closed** on the harness's own integrity failures (tamper detection).
- Exit codes are always propagated (0 pass, non-zero on miss/error), `--ci` or not.

## Portability

- **Harness-agnostic** by construction where possible; per-harness packs where required (DD-08).
- **Local-first** (no service required for core function); **CI-second**.
- Python 3.10+ core; CLI wrapper; no runtime dependency on a proprietary backend.

## Security

- Untrusted packs: sandbox (env stripping, FS isolation, optional Docker `--network none`), trust levels
  (`built-in`/`local`/`external`), audit trail, secret sanitization (PRD 06).
- Strict pack schema validation (e.g. `^[a-zA-Z0-9_-]+$` identifiers) before any path use — closes the
  predecessor's path-traversal gap.
- Signed packs + provenance on release (DD-25).

## Cost

- Deterministic oracles are free; the judge runs only where a case needs it and is cached.
- A `--max-cost` / budget governor aborts a run that exceeds its ceiling (marking remaining cases
  `aborted: cost_exceeded`), absorbed from the predecessor's field CI.

## Observability & self-check

- `agentdrill doctor` — environment/target sanity.
- `agentdrill validate --strict [--pre-flight]` — pack/target validation before a run.
- Audit log of policy/trust decisions per run.
- A shareable run summary (dimensions + honest outcome split + exit code).

## Documentation

- Every published result documents its methodology and pins so an external party can reproduce it without
  contacting us (CUJ-3).
