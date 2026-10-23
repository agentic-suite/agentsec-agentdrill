# Comparison & Attribution — Design

**BLUF:** Comparisons run against **golden expected results** (not "last run wins"), distinguish a real
defense regression from an adapter/model/**oracle** swap, and **attribute** a blocked→missed flip to the
config/pin diff that caused it (CUJ-14).

> **Status:** normative (M9). Implementation: `agentdrill/comparison/golden.py` (Golden + golden-lock),
> `golden_store.py` (`.agentdrill/goldens/`), `attack_engine.py` (case/tag/aggregate deltas),
> `change_detection.py` (adapter/model/oracle changes), `attribution.py` (attributed_to + mechanism +
> confidence), `outcome_classification.py` (three-way layer).

## Golden model

A `Golden` is a preregistered, **locked** expected result for one pack version, bound to
`pack@version+hash` and persisted under `.agentdrill/goldens/<pack@version+hash>.json`:

| Field | Meaning |
|---|---|
| `pack_ref` | `name@version+hash` the golden is bound to |
| `created` | ISO-8601 creation timestamp |
| `locked` | Always `true` — a golden is never silently overwritten |
| `pins` | The pins the golden was recorded under (M8 8.3) |
| `cases[]` | `{case_id, outcome (blocked/missed/degraded), tags[]}` |

`check_golden` compares a candidate's outcomes against the golden and **flags** every difference with a
re-pin note; the golden is never mutated.

## Golden expected results

- Preregistered, locked per pack version; **golden-lock rule** (DD-28): a result differing from its golden
  is **flagged** with a re-pin note, never silently corrected.
- Stored under `.agentdrill/goldens/`, bound to `pack@version+hash`.

## Comparison levels

| Level | Meaning |
|---|---|
| per-case | was this case better/worse? |
| per-tag / family | did a class regress? |
| aggregate | overall outcome-split delta |

## Change detection (not regressions)

| Change | Classification |
|---|---|
| Driver/target digest differs | `adapter_changed` (not a regression; `--allow-adapter-change`) |
| Model pin differs | `model_changed` (not a regression) |
| Oracle version differs | `oracle_changed` (invalidates comparability; re-baseline note) |
| Outcome flip, none of the above | a real `scenario_failed`/miss |

## Attribution

`attributed_to` correlates a blocked→missed flip with the target-config diff / pin change / adapter change
that caused it, reporting the **stage/mechanism** and a confidence — never a bare diff. Unattributable
flips are labeled `unknown` (never guessed). CI can bisect by re-running against intermediate configs.

## Outcome classification

`adapter_failed` / `agent_crashed` / `scenario_failed` (+ `blocked`/`missed`/`degraded`) so a failure is
attributed to the right layer — the predecessor's trace-diff discipline, re-pointed.
