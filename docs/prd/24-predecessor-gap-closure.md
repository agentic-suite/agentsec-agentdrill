# PRD 24 — Predecessor Gap Closure (v0.1.0)

**BLUF:** The predecessor eval harness shipped with **acknowledged, deferred gaps** — trust boundaries
never implemented (its most significant security finding), unsigned packs, no SBOM for plugins, a
`scenario_id` path-traversal vector, a flat `audit.log` without rotation or integrity, SQLite "planned"
but never shipped, and a v0.3.0 WBS that was gates-only with no new scope. agentdrill v0.1.0 closes every
one of them at the foundation — none carry forward. This is the closure ledger.

**Status:** Draft — v0.1.0 (2026-10-09) · **Owner:** @deghosal-2026 · **Parent:** agentic-suite #209

## The predecessor's acknowledged gaps → closure

| # | Predecessor gap (its own security reviews/WBS) | Severity there | agentdrill v0.1.0 closure | Where |
|---|---|---|---|---|
| **G1** | **Trust boundaries never implemented** — "all packs are treated equally regardless of origin"; deferred M8 item, called "the most significant remaining security gap" | Critical | **Delivered at foundation:** `built-in`/`local`/`external` trust levels enforced at load/run; `external` packs are sandbox-restricted (subprocess-only), never benchmark-published | [PRD 17](17-pack-registry-and-governance.md), [PRD 06](06-security-baseline.md) F15 |
| **G2** | **Unsigned packs from external sources** — "FUTURE: consider signature verification"; registry poisoning unhandled | High | **Delivered:** Sigstore signing + verified publishers + `pack verify` before install; index entries signed; takedown recorded on the signature chain | [PRD 11](11-decisions.md) DD-25, [PRD 17](17-pack-registry-and-governance.md), F35/F39 |
| **G3** | **`scenario_id` path traversal** — identifier used unsanitized in artifact filenames | Critical (fixed late there) | **Never opens:** strict `^[a-zA-Z0-9_-]+$` validation at pack load, before any path use — an invariant (PRD 15), tested in the meta-verification pack | [PRD 15](15-data-model.md) §Invariants, [PRD 21](21-pack-catalog.md) pack 3 |
| **G4** | **Audit log: no rotation, no integrity, single file grows unbounded** | Medium | **Delivered:** size-capped + rotated audit + hash-chained entries (agentwatch store discipline); tamper = fail-closed | [PRD 06](06-security-baseline.md), [PRD 13](13-non-functional-requirements.md) |
| **G5** | **Env-only sandbox insufficient for third-party packs** — "no filesystem isolation, no network restriction; a malicious agent in sandbox mode still has full FS/network access; OS-level sandboxing should be added" | High | **Delivered for packs (executable content):** Docker/OS-level isolation (`--network none`, read-only root, resource caps) *required* for `external` trust level — the predecessor's own recommendation, made mandatory | [PRD 06](06-security-baseline.md), F15 |
| **G6** | **No SBOM / dependency-risk tracking for plugins** — "FUTURE: SBOM for plugin packages" | Medium | **Delivered:** SBOM + provenance on every release (org governance floor); plugin/pack installs resolve against it | [PRD 11](11-decisions.md) DD-25, [PRD 07](07-success-metrics.md) gate item 11 |
| **G7** | **SQLite "planned for v0.2"** → never shipped; local JSON only | Low | **Waived by design:** local JSON + the fleet/trend stores cover v0.1.0 needs; a database backend is a non-goal until a real workload demands it (documented, not silent) | [PRD 14](14-non-goals.md) |
| **G8** | **Per-adapter sandbox profiles** — "FUTURE: evaluate need as adapter count grows" | Low | **Delivered as policy, not per-adapter sprawl:** trust-level × target/driver matrix (one trust policy, all adapters) — the matrix replaces per-adapter hand-rolls | [PRD 06](06-security-baseline.md) |
| **G9** | **Field harness vs product runs confusion** — `MockJudge` leaked into product paths; field results mistaken for product evidence | Process | **Never opens:** attestation levels (`mock`/`fixture`/`live`, F63) make the distinction machine-enforced — `mock`-attested runs cannot publish; demo watermarked `never evidence` | [PRD 20](20-efficacy-freshness-lifecycle.md) F63/F66 |
| **G10** | **Exit-code + scoring theater classes** (#269/#270-class: silent pass-everything gates, crashed agents scoring green) | Critical (fixed late there) | **Never opens:** the meta-verification pack (F43, [PRD 21](21-pack-catalog.md) pack 3) ships in v0.1.0 CI — these classes are regression-tested *in the release gate itself*, not patched after discovery | [PRD 21](21-pack-catalog.md), [PRD 19](19-detection-validation-bas.md) |
| **G11** | **Rubric criteria as dead text** (#273-class: judge never sees the criteria; criteria are decoration) | High (fixed late there) | **Never opens:** criteria-interpolation is a meta-verification case; judge prompts are hashed into the manifest (F81) — a criteria-path change is a pin change | [PRD 23](23-oracle-credibility.md) F81, [PRD 21](21-pack-catalog.md) |
| **G12** | **Model-mismatch 404s** — agents hardcode vendor models; local endpoints fail opaquely | Medium | **Delivered:** targets/drivers declare `model` + `base_url` in the target config; recon (F42) fails loudly on unreachable model surfaces before cases run; model pin is manifest-mandatory | [PRD 02](02-architecture.md), F42, [PRD 13](13-non-functional-requirements.md) |
| **G13** | **Nested-repo / PYTHONPATH drift in harness setup** — silent no-op `uv sync`, shadowed modules | Low | **Delivered:** the demo stack (F66) + target config carry their own environment resolution; recon snapshots record the resolved env in the manifest so drift is visible per run | F42/F66, [PRD 15](15-data-model.md) |
| **G14** | **Bounded-by-cost runs** — cost governor existed but per-suite budgets were ad hoc | Low | **Delivered:** per-case `budget` + run-level `--max-cost` inherited; exceeded → `aborted: cost_exceeded`, published as part of the run shape (never hidden) | [PRD 13](13-non-functional-requirements.md) §Cost |

## What this PRD is not

- **Not a porting plan** — the predecessor is retired and its harness mechanics are already absorbed
  ([PRD 10](10-feature-parity.md)). This PRD exists so its *self-declared* gaps are visibly closed or
  waived in one place, at the foundation, rather than rediscovered under pressure.
- **Not new scope creep into v0.1.0** — every closure above rides an existing v0.1.0 feature (F-numbers
  cited); G7 is the only **waived** item, and it is waived with a written reason, not forgotten.

## Reviewer check

For each row: the closure must already exist in this PRD set (cite above) — **or the gap carries into
agentdrill with an owner and a version.** As of this draft, zero open carryovers.