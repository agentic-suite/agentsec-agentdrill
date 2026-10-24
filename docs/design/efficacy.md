# Efficacy Control & Utility — Design

**BLUF:** The control group that makes the benchmark scientific. Every case runs against an **unguarded
twin**; only **efficacy-verified** cases count (inert attacks flagged `attack_inert`, excluded from rates).
Every enforced case also carries a **benign twin** so a `blocked` number publishes its **utility price tag**.

> **Status:** normative (M13). Implementation: `agentdrill/efficacy/` — `control.py` (unguarded twin,
> F59), `inert.py` (`attack_inert` + rates), `utility.py` (utility-under-attack, F51), `cleanup.py`
> (`dirty_target`, F50), `report.py` (per-case efficacy artifact). Reference:
> [efficacy-and-utility](../reference/efficacy-and-utility.md).

## Efficacy control (F59)

| Unguarded | Guarded | Meaning |
|---|---|---|
| success | blocked | true positive for the control |
| success | missed | **real miss** (the finding that matters) |
| failure | any | the case is **inert** → flagged `attack_inert`, excluded from rates, never pads a green table |

Efficacy is verified per pack release **and on target change** (a config change can inert an attack as
easily as block it). The efficacy run ships in the evidence bundle (CUJ-11/CUJ-19).

## Utility-under-attack (F51)

Every attack case links a `benign_twin`; the report publishes:

- **benign utility** — does the stack pass the benign twin?
- **utility under attack** — benign utility while attacks are in play.
- **enforcement rate** — blocked / (blocked + missed).

A defense with high enforcement + collapsed utility-under-attack gets a `utility_cost` finding —
**agentdrill never lets a "100% blocked" number stand without its price tag.**

## Cleanup (F50)

Every case declares cleanup; it runs after every case including failed/timeout ones. A cleanup failure is a
**release-blocking `dirty_target`** finding — a dirty target makes every later number untrustworthy
(Caldera/ART discipline, ported to agent defense).

## Why this is the differentiator

No agent-security benchmark runs an unguarded control group. Without it, "blocked" is unmeasured; with it,
every number is *scientific* rather than rhetorical — the SWE-Bench flawed-tests lesson applied up front.
