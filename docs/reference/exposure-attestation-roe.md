# Exposure Ledger, Drill Attestations & Rules of Engagement — Reference

**BLUF:** Make the gate livable, the proof consumable, and the tool safe to run anywhere. A findings
**ledger** with time-boxed **waivers** that never relabel a miss; signed **drill attestations** with
freshness; and **Rules of Engagement** with a fail-closed preflight and safe-fire interlocks. **Normative
(M28).** Packages: `agentdrill/ledger/`, `agentdrill/attestations/`, `agentdrill/roe/`. Source design:
[design/exposure-attestation-roe.md](../design/exposure-attestation-roe.md); PRD
[33](../prd/33-exposure-ledger-and-waivers.md) (R69), [34](../prd/34-drill-attestations-and-deploy-gate.md)
(R70), [35](../prd/35-rules-of-engagement-and-safe-fire.md) (R71). Closes gaps G9, G10, G11.

## Exposure ledger & waivers (`agentdrill/ledger/`)

```
lifecycle: open → triaged → fix_in_progress → fixed → verified_fixed → decayed
side:      accepted_risk | false_positive | wont_fix
```

| Concern | API | Notes |
|---|---|---|
| Lifecycle | `open_finding`, `transition` | `fixed → verified_fixed` requires verification (**verified, not believed**); the honest `outcome` is **immutable** |
| Store | `Ledger` | records findings and **never hides** one |
| Per-finding severity | `SeverityVector` (CVSS v4.0 + AIVSS) | `composite_score` **refuses** — never aggregated |
| Waiver | `create_waiver` (90 d; **30 d** critical), `sync_waivers`, `require_known_miss_budget`, `require_waivable` | **annotates** `waived:<id>`, **never relabels**; **auto-reopens** on expiry; **integrity findings not waivable**; `sign_waiver`/`verify_waiver` |
| Exports | `export_sarif`, `export_oscal_poam`, `export_oscal_assessment_results`, `ticket_updates` | reuse the M26 emitters (SSOT); `to_waiver_record` **re-points** M26's waiver seam here |

**Policy.** A waiver carries scope/tier/reason/**drilled compensating control**/approvers/**expiry**/drift
trigger/residual risk. Gate impact may drop; **visibility never**. An expired waiver **never suppresses**
(verified in the SARIF export). The **known-miss budget** gates the release on unwaived misses.

## Drill attestation (`agentdrill/attestations/`)

```
predicate: agentdrill/drill-result/v1  (in-toto)
subject:   { name: agentdrill-drill, digest: { sha256: <config_digest> } }
predicate: packs@ver/hash · tiers/k · outcomes+CIs · witness_coverage ·
           live|fixture|mock · oracle_versions · known_misses/waivers · lab ·
           standards_pins · issued · expires · not_drilled[]
signature: HMAC-SHA256 (Sigstore-envelope shaped; Rekor in deployment)
```

- `build_statement` refuses an empty `not_drilled` and any **non-evidence** realness (`mock`/`fixture`).
- `verify_statement` is fast and **forgery-rejecting**; `assess` verifies + freshness-checks + evidence-checks
  and serves the **4 reference consumers** — `cli`, `github-action`, `k8s-admission`, `agentgate`.
- **Auto-invalidate** (`check_freshness`): config-digest change · security-deprecated pack · relevant new
  incident · oracle **major** bump (patch is fine) · waiver expiry · the attestation's own expiry.
- A valid attestation is **not** "secure": scope/tier/limits and the `not_drilled` list are always foregrounded.

## Rules of engagement (`agentdrill/roe/`)

The RoE is signed and versioned: targets+ownership · env class (`ephemeral|purple|prod`) · allowed effect
classes · **canary-only** · windows · rate/cost ceilings · blast-radius caps · tier ceiling · approvers ·
contacts · abort conditions.

**Fail-closed preflight** (`preflight`) refuses with a named reason: `roe_unsigned`, `target_out_of_scope`,
`ownership_unverified`, `effect_class_not_allowed`, `env_would_not_permit_effect` (a **prod** env never
permits destructive effects), `canary_required`, `outside_window`, `rate_ceiling_exceeded`,
`cost_ceiling_exceeded`, `blast_radius_cap_exceeded`, `tier_ceiling_exceeded`, `third_party_hosts_resolvable`,
`witness_unhealthy`, `cleanup_unverified`. `scope_receipt`/`verify_receipt_chain` produce a hash-chained
per-action audit.

**Interlocks:** `AbortController` — a **global abort** independent of the in-band agenthalt (immediate,
idempotent); `DeadManSwitch` — a lost heartbeat trips; `check_rate_watchdog`/`check_cost_watchdog`;
**`verified_teardown`** — a `dirty_target` (M13) is **release-blocking**; `require_egress_consent` — nothing
leaves the machine without consent.

## Known limitations

- Local signing is HMAC (Sigstore-envelope shaped); a real deployment records signatures in a transparency log.
- The ledger is a local store at v0.1.0 (SQLite/GRC sync is a deployment choice); waiver approval RBAC is
  external (recommended: signed approvals from an external IdP).
- Abort p95 ≤ 5 s, teardown ≥ 99 % and intake SLAs are **operational** — measured in the M31 field tests.
