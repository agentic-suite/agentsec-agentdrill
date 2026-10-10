# Comparison & Attribution — Design

**BLUF:** Comparisons run against **golden expected results** (not "last run wins"), distinguish a real
defense regression from an adapter/model/**oracle** swap, and **attribute** a blocked→missed flip to the
config/pin diff that caused it (CUJ-14).

> **Design intent** (pre-build). WBS M9.

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
