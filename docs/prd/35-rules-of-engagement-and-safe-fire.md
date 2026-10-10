# PRD 35 — Rules of Engagement & Safe-Fire Interlocks

**BLUF:** agentdrill makes agents attempt destructive and exfiltrating actions against real stacks; a mis-scoped run is a **reportable incident**. Add a signed **Rules-of-Engagement** file, a **fail-closed preflight** check on every case, hard invariants (canary-only destructive effects; no third-party targets; default-deny on prod), and **interlocks** (global abort independent of the system under test, dead-man switch, watchdogs, verified teardown). This also mitigates the dual-use risk: a tool with authorization and audit is categorically different from an arsenal.

**Status:** Draft — v0.1.0 addition (2026-10-10) · **Owner:** @deghosal-2026 · **Parent:** agentsec-ecosystem #209 · **Features:** F97 · **Reqs:** R71

## Why

- Today's safeguards are *sandboxing for untrusted packs* (protects us from packs) and *cleanup* (F50). Nothing protects the **target and bystanders from us**.
- Microsoft's own guidance is a **purple environment** (non-prod, prod-like); pentest has Rules of Engagement; BAS markets "production-safe."
- Enterprise buyers and legal will demand authorization, scope, and abort.
- Mitigates RK-2/RK-13 (dual-use) and RK-8 (untrusted packs).

## Requirements (v0.1.0)

| # | Requirement | Acceptance criterion |
|---|---|---|
| **R71** | A signed **RoE** is required for any non-demo run; a **fail-closed preflight** refuses out-of-scope cases; **interlocks** (abort, dead-man, watchdog, verified teardown) are mandatory; per-action **scope receipts** are hash-chained. | Zero out-of-scope actions; 100% of planted out-of-scope attempts refused; abort p95 ≤ 5 s; teardown verified clean ≥ 99%. |

## Features

| # | Feature | Req | Notes |
|---|---|---|---|
| **F97** | **Rules of engagement & safe-fire**: RoE (authorized targets + ownership proof, environment class `ephemeral/purple/prod`, allowed effect classes, canary-only data limit, windows, rate/cost ceilings, blast-radius caps, tier ceiling, approvers, contacts, abort conditions); preflight; interlocks; scope receipts; verifier checks | R71 | Consumes F50/F63/F64; enforces [PRD 26](26-independent-effect-witness.md) canary invariant; consumes [PRD 27](27-adversary-lab.md) isolation |

### Hard invariants
1. **Destructive/exfil effects target canaries or ephemeral clones only**; production real data is never an attack object.
2. **No third-party infrastructure** unless ownership is verified.
3. `prod`: default-deny; two-person approval; shorter windows; T0/T1 only.
4. **Consent gate** for any attack content leaving the machine (hosted models/APIs).

### Interlocks
**Global abort** independent of agenthalt (the thing under test must not be the thing that stops the test); **dead-man switch** (lost heartbeat → abort + cleanup); **watchdogs** on cost/rate; **cleanup verification** with teardown receipts (`dirty_target` is release-blocking).

## CUJs

### CUJ-48 — Authorized to fire
Sign an RoE: purple tenant only, canary data only, Tue–Thu 02:00–06:00, T2 max, $50 cap. **Success:** any out-of-scope attempt is refused and logged.

### CUJ-49 — Abort in seconds
A drill hammers staging; one command aborts in <5 s; teardown receipts show clean. **Success:** abort p95 ≤ 5 s.

## Success metrics

| Metric | Target |
|---|---|
| Out-of-scope actions executed | **0** (release-blocking) |
| Preflight negative-test suite (planted out-of-scope refused) | 100% |
| Global abort latency (command → all attack traffic stops), p95 | ≤ 5 s |
| Dead-man-switch trigger-to-halt | ≤ 30 s |
| Teardown verified clean (receipts) | ≥ 99% (else `dirty_target`) |
| Non-demo runs with a signed RoE | 100% |
| `prod` runs without two-person approval | **0** |
| Hosted-model/API egress without consent | **0** |
| Third-party-host contact (network-capture verified) | **0** |
| Time to author an RoE from a template | ≤ 15 min |

## Dependencies
F50, F63, F64 · [PRD 26](26-independent-effect-witness.md), [PRD 27](27-adversary-lab.md), [PRD 41](41-platform-compatibility.md) (tenant/ownership checks).

## Boundaries & non-goals
- RoE strength is bounded by ownership verification (DNS/cloud-account/ARN/control-file).
- Safety friction is offset by templates and a `local-demo` fast path (watermarked non-evidence).
- Not an enforcement control; it constrains *our own* firing.

## Open questions
1. Ownership-verification methods per target class.
2. Is T3 permitted in v0.1.0? (Recommend: defer; ship T0–T2.)
