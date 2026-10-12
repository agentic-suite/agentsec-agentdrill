# PRD 20 — Efficacy, Freshness & Lifecycle (closing the critical gaps)

**BLUF:** Four gaps would make everything else theater if left open: (1) **pack efficacy** — a `blocked`
number is meaningless unless the attack demonstrably succeeds against an *unguarded* stack (the control
group no agent-security benchmark runs); (2) **freshness** — "replays documented incidents" decays without
a disciplined incident-intake pipeline; (3) **fix-validation** — a remediation that silently decays is a
miss we caused; (4) **seams** — attacks that traverse multiple enforcers probe the gaps *between*
controls, where composition fails. Plus the honesty mechanics that close the rest: target attestation,
a standalone verifier, evidence privacy, and a first-run demo stack.

**Status:** Draft — v0.1.0 (2026-10-09) · **Owner:** @deghosal-2026 · **Parent:** agentic-suite #209 · Features: F59–F66

## F59 — Pack efficacy control (the unguarded control group)

The single most important missing feature in the entire category. A defense benchmark that never proves
its attacks *work* measures nothing — "100% blocked" against an attack that would have failed anyway is
scoring theater of exactly the kind [PRD 14](14-non-goals.md) forbids.

- Every pack carries an **efficacy run**: the same cases against the same target with the named enforcers
  **disabled** (or an unguarded twin target).
- A case is **efficacy-verified** only if it *succeeds* unguarded. Its guarded result is then meaningful:
  - unguarded success + guarded block = true positive for the control.
  - unguarded success + guarded miss = **real miss** (the finding that matters).
  - unguarded failure = the case is **inert** — flagged `attack_inert`, excluded from enforcement rates,
    never published as coverage. **An inert case cannot silently pad a green table.**
- Efficacy is verified **per pack release** and on **target change** (a config change can inert an attack
  as easily as block it).
- Published tables mark every case with its efficacy status; the efficacy run ships in the evidence
  bundle (CUJ-11).

> This is the control group that makes the whole honest-benchmark story *scientific* rather than
> rhetorical. SWE-Bench's flawed-tests discovery (59.4% of hard tasks) is what happens without it.

## F60 — Incident-intake pipeline (freshness)

LiveCodeBench's lesson: static benchmarks rot; the value is in the intake cadence.

1. **Watchlist** — automated monitoring of the documented-incident sources (vendor blogs, Invariant-class
   research, CAISI/AISI advisories, CVE feeds for agent tooling, the ecosystem harness watchlist).
2. **Triage** — a new incident enters a public tracker with an SLA: **assessed in 7 days, pack draft or
   explicit "not-applicable" with reason** — mirrors the misses-within-7-days commitment on the results
   side.
3. **Pack draft** — authoring SDK (F46) scaffolds the case from the incident report; `incident_ref`
   mandatory; efficacy control (F59) mandatory before merge.
4. **Review → registry** — the [PRD 17](17-pack-registry-and-governance.md) flow; dark-holdout copies
   added where the incident class permits.
5. **Deprecation freshness** — packs whose incident patterns become structurally impossible on current
   stacks (harness patched it) are **deprecated with a note**, not kept to inflate green rows.

## F61 — Remediation validation lifecycle ("fixes hold")

Straiker's continuous-testing insight, as a lifecycle: a remediation is not done when it ships — it's done
when it *holds*.

- Every confirmed miss that gets fixed gets a **fix-validation case**: the original case, pinned to the
  fix commit, becoming a **permanent regression case** in the pack.
- The CI gate runs fix-validation cases on **every** subsequent policy/config release — decay of a
  shipped fix is a release-blocking finding (`fix_decay`), with attribution (F38) naming what decayed it.
- The [closes-the-loop policy suggestion](05-features.md) (F21) output explicitly includes: *the
  fix-validation case that will guard this fix forever*.

## F62 — Cross-defense seam probing

Controls are tested individually; incidents traverse seams. Two mechanisms:

- **Denied-then-retried** (from the agentwatch pattern inventory): the attack is blocked by control A and
  immediately re-attempted via a different route (different tool, encoding, transport). A stack that
  blocks N isolated routes but leaves route N+1 open shows a per-control green table and a real chain
  miss.
- **Composition cases**: pack cases whose `target` lists *multiple* enforcers, with per-stage oracles
  declaring which control is expected to stop which hop — the gap where "gate denies, but belt allows the
  same action via a different process" lives.
- Findings are typed `seam_gap` with the two (or more) controls named; these feed the heat-map (F53) as
  `partial` at the composition level.

## F63 — Target attestation (what was actually real?)

"Deployed stack" is claimable too loosely. Every target config declares, per component:

| Attestation level | Meaning |
|---|---|
| `live` | The real component, really enforcing (production or staging config) |
| `fixture` | Real component, fixture/replay inputs (deterministic mode) |
| `mock` | A stand-in implementing the contract |

- Results are **labeled with the weakest attestation level in their target chain** — a run against a mock
  PDP can never publish as if it drilled the real PDP.
- `mock`-attested results are excluded from BenchmarkReleases entirely (they are authoring aids, not
  evidence); `fixture` results publish with the label visible.
- The attestation block ships in the run manifest; the meta-verification suite (F43) includes cases
  trying to *forge* attestation levels.

## F64 — Standalone verifier

The agentwatch verifier pattern, applied to our artifacts: a **zero-install, offline verifier** for
benchmark releases and evidence bundles.

- Given a bundle (or a published release), it checks: signature chain (F35), manifest completeness (F36),
  hash bindings (pack@version ↔ numbers), efficacy labels (F59), attestation labels (F63), statistical
  shape (F29/F55: no bare percentages), and reproduces verdict *integrity* (not the run itself).
- Output is three unambiguous verdicts — **intact / complete / honest-shaped** — plus the first broken
  link named on failure. A reviewer, journalist, or auditor needs no agentdrill install and no network.

## F65 — Evidence privacy & redaction receipts

Evidence bundles contain target internals (system prompts, config, tool schemas). Sharing a finding must
not leak the target's secrets.

- Bundles apply the agentwatch redaction posture to target-side content: secrets/PII redacted **before
  bundling**, with **redaction receipts** (what class was redacted, how many, where) recorded in the
  bundle — the recipient can see *that* something was redacted without seeing *what*.
- The verifier (F64) validates receipts against the redaction policy, so a bundle can't smuggle content
  out or hide evidence behind bogus redactions.

## F66 — Demo stack & quickstart

The ≤15-minute promise needs a first run that doesn't require a deployed stack:

- `agentdrill quickstart` boots a **bundled demo target** (small local stack: a demo policy bundle, a demo
  agent loop, a stub gate) and runs a mini pack against it — the user sees blocked/missed/kill-time
  output, the honest table, and an evidence bundle in minutes.
- Demo results are `mock`-attested (F63) and watermarked `demo — never evidence`, the same discipline as
  agentwatch's synthetic demo bundle.
- Then `agentdrill init` scaffolds wiring their *real* stack — the adoption path is quickstart → init →
  first live drill.

## Traceability additions

| Req | Feature | Test |
|---|---|---|
| R33 Pack efficacy | F59 | Efficacy run per pack release; inert cases excluded from enforcement rates |
| R34 Freshness | F60 | New incident assessed ≤7 days (pack draft or N/A + reason) |
| R35 Fix validation | F61 | `fix_decay` release-blocking; fix case pinned to fix commit |
| R36 Seam probing | F62 | `seam_gap` findings name the controls involved |
| R37 Attestation | F63 | Weakest-link label; `mock` excluded from benchmark |
| R38 Verifier | F64 | Clean-machine, offline, three-verdict output |
| R39 Bundle privacy | F65 | Redaction receipts verified in bundles |
| R40 Quickstart | F66 | ≤15 min to first honest result, demo-watermarked |

## Sequencing within the program

All of F59-F66 land in **v0.1.0**. F59 (efficacy), F63 (attestation), and F66 (quickstart) are the credibility floor of the first published table; F60 (intake), F61 (fix-validation), and F65 (receipts) ship with the first release; F62 (seams) and F64 (verifier) land together — the verifier ships with the first published release, ready for the first external reproduction request
  arrives in earnest.
