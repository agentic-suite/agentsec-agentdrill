# Self-Attack & Meta-Verification — Reference

**Status:** normative (M14). Suites: `self-attack/`. Logic: `src/agentdrill/security/`. Design:
[../design/threat-model.md](../design/threat-model.md). PRD: [06 security baseline](../prd/06-security-baseline.md).

**Self-attack is shipped, not optional** (R7); a tamper regression is release-blocking.

## Evasion / self-attack pack (14.1)

`self-attack/evasion-self-attack.yaml` red-teams the ecosystem's **own** tools. `EVASION_ATTACKS`:

| Case id | Attack |
|---|---|
| `pack-tamper` | tamper a pack so a blocked attack reads blocked-but-isn't |
| `hook-disable` | disable the enforcement hook to skip a pack |
| `policy-edit` | edit compiled policy to always-allow |
| `telemetry-injection` | inject telemetry via crafted tool names/args |
| `evidence-edit` | edit a published result / evidence record |
| `update-hijack` | hijack the update channel with a hostile pack set |
| `agent-instructed-evasion` | instruct the agent to evade the guard |

`assert_fail_closed(pack)` fails loudly (`SelfAttackError`) unless every case expects `blocked` on an
`enforcement` or `integrity` dimension.

## Drill-the-drill (14.2, F43)

`agentdrill/security/meta_verification.py` checks the oracle engine and gate:

| Check | Catches |
|---|---|
| `check_no_vacuous_block` | a vacuous no-op scored `blocked` |
| `check_must_block_exits_nonzero` | a silent pass-everything gate |
| `check_fixtures_intercept` | a live call in fixture mode |
| `check_no_forged_attestation` | a claimed ≠ actual attestation level |
| `check_no_severity_gaming` | a severity weaker than the rubric |

`require_meta_clean(findings)` raises `MetaVerificationError` if any check is gamed.

## Dark holdout (14.3, F33)

`check_holdout(pack_ref, published_green=, holdout_green=)` → `HoldoutResult`; `gaming` = published green
but holdout red. `require_no_gaming` raises `PackGamingError` (release-blocking). `HoldoutRegistry` keeps
the private holdout subset; `published_ids(all_ids)` excludes it.

## CI cadence (14.4)

`CADENCE_SUITES = ("evasion", "meta", "holdout")`; `run_cadence(release, runners)` runs each and a
missing/red suite raises `CadenceError` (`require_cadence_green`). `publish_cadence(result)` publishes
the record per release.

## Hidden adversarial case (14.5)

`self-attack/meta-verification.yaml` holds an independent-reviewer-authored **secret** case
(`hidden-adversarial`) tagged `hidden`. `escapes_single_layer(present_layers)` is `True` unless **every**
layer in `HIDDEN_REQUIRED_LAYERS` is present — no single control stops it.
