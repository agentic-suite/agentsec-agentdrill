# Exposure Ledger, Drill Attestations & Rules of Engagement — Design

**BLUF:** Make the gate livable, the proof consumable, and the tool safe to run anywhere. A findings
**ledger** with time-boxed **waivers** that never relabel a miss; signed **drill attestations** with
freshness; and **Rules of Engagement** with fail-closed preflight and safe-fire interlocks. WBS
[M28](../wbs/v0.1.0/wbs-v0.1.0-part15-context-governance.md). Reference:
[PRD 33](../prd/33-exposure-ledger-and-waivers.md), [PRD 34](../prd/34-drill-attestations-and-deploy-gate.md),
[PRD 35](../prd/35-rules-of-engagement-and-safe-fire.md).

> **Built (M28).** Packages: `agentdrill/ledger/` (`finding.py`, `ledger.py`, `waivers.py`, `exports.py`),
> `agentdrill/attestations/` (`drill.py`, `freshness.py` — plural, since the M5 `attestation.py` module
> exists), `agentdrill/roe/` (`rules.py`, `interlocks.py`). See the
> [reference](../reference/exposure-attestation-roe.md). Rewritten against the built system at M31–M32.

## Exposure ledger & waivers (F95)

```
lifecycle: open → triaged → fix_in_progress → fixed → verified_fixed → decayed
side:      accepted_risk | false_positive | wont_fix
```

A **waiver** carries scope, tier, reason, **drilled compensating control**, approvers, **expiry** (default
90 d; critical 30 d), drift trigger, residual-risk statement — and **auto-reopens** on expiry/drift.

**Invariants (anti-theater):** the label stays `missed` (a waiver adds `waived:<id>`, never relabels);
gate impact may drop, **visibility never**; a **known-miss budget** gates the release; waivers are signed +
hash-chained + verifier-checked; **integrity findings are not waivable**. Exports: OSCAL POA&M/assessment-
results; SARIF `suppressions` (`external`).

## Drill attestations (F96)

```
predicate: agentdrill/drill-result/v1  (in-toto)
subject:   config_digest
predicate: packs@version/hash · tiers/k · outcomes+CIs · witness_coverage ·
           live|fixture|mock · oracle_versions · known_misses/waivers · lab · standards_pins ·
           issued · expires
signature: Sigstore (+ transparency log)
```

Auto-invalidate on: config-digest change · security-deprecated pack · relevant new incident unrun · oracle
major bump · waiver expiry. Reference consumers: CLI `verify`, GitHub Action, K8s admission policy
(Kyverno/OPA-Gatekeeper-class), `agentgate` start-time check. **mock/fixture = non-evidence**; the predicate
always lists **what was NOT drilled**.

## Rules of engagement (F97)

```
RoE: targets+ownership · env_class(ephemeral|purple|prod) · allowed_effect_classes ·
     data_limit(canary_only) · windows · rate/cost_ceilings · blast_radius_caps ·
     tier_ceiling · approvers · contacts · abort_conditions        (signed, versioned)
```

**Preflight (fail-closed):** target in scope · ownership verified · env permits effect class · canary-only ·
rate/cost headroom · no third-party hosts resolvable · witness healthy · cleanup path verified → else the
case **refuses to fire**.

**Interlocks:** **global abort** independent of agenthalt; **dead-man switch** (lost heartbeat → abort +
cleanup); rate/cost watchdogs; **verified teardown** (`dirty_target` is release-blocking); per-action **scope
receipts** (hash-chained audit); **consent gate** for any attack content leaving the machine.

## Invariants

1. Zero out-of-scope actions.
2. Waivers never relabel; integrity findings not waivable.
3. A valid attestation ≠ "secure" — scope/tier/limits always foregrounded.

## Open questions
1. Owning-verification methods (DNS TXT, signed repo file, cloud tag, org SSO).
2. Waiver approval via in-tool RBAC vs. external GRC (recommend external-IdP signed approvals).
3. Propose the attestation predicate to in-toto after a design-partner pilot.
