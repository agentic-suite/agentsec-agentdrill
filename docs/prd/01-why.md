# PRD 01 — Why

**BLUF:** Agent-security products oversell detection and nobody publishes reproducible evidence of what
their controls actually stop. Red-team tooling is OSS-strong but **offline and point-in-time**. Nothing
treats agent **policies as continuously regression-tested code**. agentdrill is that missing layer: the
ecosystem's proof-of-work engine. It **absorbs the red-team predecessor idea** and the eval-harness patterns of the
shipped/retired **predecessor eval harness (retained privately)**.

**Status:** Draft — v0.1.0 (2026-10-09) · **Owner:** @deghosal-2026 · **Parent:** agentsec-ecosystem #209

## The problem

1. **Detection is oversold and unverifiable.** Vendors claim coverage; almost none publish reproducible
   numbers for what their controls stop.
2. **Red-teaming is point-in-time.** PyRIT, garak, promptfoo, and AgentDojo are strong OSS tools, but they
   are run ad hoc, offline, against a snapshot. None run attacks against your **live policy stack
   continuously, like unit tests**.
3. **Policies ship without regression tests.** The ecosystem compiles and enforces policy (agentpolicy →
   policyweave → enforcers), but a policy PR can silently un-block a known attack pattern. There is no
   pass/fail gate that says *"this rule change lets attack X through."*
4. **The ecosystem's own claims depend on this.** Every other tool's acceptance criteria reference "attack
   packs." Without a place where those packs live and run, the ecosystem's claims are as hollow as
   everyone else's.

## Evidence from the landscape

| Evidence | Source |
|---|---|
| ~46% ASR against some best-known defenses | [AgentDojo](https://arxiv.org/abs/2406.13352) |
| One hacking prompt nearly doubles ASR (GPT-4 ReAct) | [InjecAgent](https://arxiv.org/abs/2403.02691) |
| Credible defenses are architectural; none "solve" injection | [arXiv 2506.08837](https://arxiv.org/abs/2506.08837) |
| Injection exploited in production (Sept 2026) | [Anthropic threat-intel](https://www.anthropic.com/threat-intelligence-report-september-2026) |
| 9 documented incidents to replay | The incident register (primary sources cited inline below) |

The incident register supplies the first packs: Slack-AI data exfiltration, MCP tool poisoning,
rug-pull/cross-server shadowing, Replit destructive-command, Plugin4Shell supply-chain RCE, and
credential-evasion attempts.

## What agentdrill is

> **"Security tools claim; agentdrill proves."**

The **proof layer**: run reproducible, versioned incident-replay **attack packs** against the *deployed*
stack in CI; publish honest, reproducible results per release; verify **kill-time** (revocation latency),
not just detection. Framework-agnostic; local-first, CI-second.

## What this supersedes / absorbs

| Absorbed | What it was | What agentdrill takes from it |
|---|---|---|
| **the red-team predecessor idea** | Adversarial-testing idea | The attack-pack + continuous-red-team framing |
| **the predecessor eval harness** (shipped, retired) | Framework-agnostic eval harness | The harness mechanics — pack format, adapter contract, runner, scoring engine, fixture/ToolStub determinism, baseline/comparison, three-gate CI, plugin registry, sandbox/trust/audit — re-pointed from *agent quality* to *defense effectiveness* ([PRD 10](10-feature-parity.md)) |

The ecosystem thesis is **unification**: one install, one record format, one proof loop.

## Why now

The ecosystem is at **Wave 0**: agentwatch, agentpolicy, agentkeys, agenthalt, and agentdrill ship together
as the thin-slice meta-MVP. agentdrill is what makes the other four's claims credible — and the coverage
row (OSS "tooling for researchers") is converting into a **security-config regression suite** that is
currently unowned.

## What success looks like

A third party re-runs our published benchmark against the published pinned config and gets the **same
numbers** — misses included — and a policy PR is rejected by CI because a drill caught a regression the
author didn't. See [PRD 04](04-users-and-cujs.md) and [PRD 07](07-success-metrics.md).

## Non-goals

agentdrill **records/proves and does not enforce**. No injection-detection claims; no model-attacking
capability development; no proprietary scoring. Full list in [PRD 14](14-non-goals.md).
