# PRD 00 — Press Release / FAQ

**BLUF:** agentdrill runs curated, versioned **incident-replay attack packs** against your *deployed*
agent-security stack in CI and publishes **reproducible, honest** pass/fail results per release — including
the attacks it did **not** stop — plus **kill-time** verification. It is the proof layer of the
agentsec-ecosystem: every other tool's "it stops X" claim is only as good as the drill that tests it.

**Status:** Draft — v0.1.0 (2026-10-09) · **Owner:** @deghosal-2026 · **Parent:** agentsec-ecosystem #209

## Press release

### agentdrill — prove what your agent defenses actually stop

*Open-sourced today, agentdrill replays the attacks that actually happened against your exact deployed
configuration, in CI, and publishes the results — the misses included.*

Every agent-security vendor oversells detection. The public benchmark record is brutal: simple prompt
injection retains roughly **46% attack-success rate** against some of the best-known defenses
(AgentDojo), and a single hacking prompt nearly **doubles** the ASR against GPT-4 ReAct agents
(InjecAgent). Meanwhile nobody publishes reproducible numbers for what their own controls actually stop.

agentdrill changes the question from *"does your tool detect attacks?"* to *"show me the drill, run it on
my machine, and let me read the result."* It is a curated, versioned library of **attack packs** — each one
a replay of a documented incident pattern (destructive-command agents, MCP tool poisoning, supply-chain
RCE, exfiltration chains, credential evasion) — run against your **deployed** stack rather than a
simulation: the MCP proxy, the credential broker, the process-confinement layer, the compiled policy, and
the halt path you actually run.

Results are public, reproducible, and honest. Each release publishes which attacks were blocked, which
were **not**, and how long revocation actually took. A third party can re-run the same pinned pack against
the same pinned targets and get the same numbers.

> *"Security tools claim; `agentdrill` proves."*

**How it works**

1. Pick a pack (or import one from promptfoo, garak, AgentDojo, or PyRIT).
2. Point agentdrill at your deployed stack.
3. Run it locally, or gate it in CI so a policy change that un-blocks an attack is rejected before merge.
4. Read the honest result: blocked, missed, degraded — plus kill-time verification.

**Availability:** installable via `pip install agentsec-agentdrill`, source under Apache-2.0 on GitHub.
v0.1.0 targets **≥2 Tier-1 coding-agent harnesses** per the ecosystem harness-compatibility matrix
(published with each release as the compatibility table — [PRD 05](05-features.md) §Compatibility).

## FAQ

**Is agentdrill another red-team arsenal?**
No. It **replays documented incident patterns**; it does not develop novel model-attacking capability.
Packs are executable security claims, reviewed like code. The dual-use boundary is an explicit open
question ([PRD 08](08-risks.md)).

**Does it claim to detect or solve prompt injection?**
No. agentdrill measures **your enforcement controls**, never "injection solved." No injection-detection
claims are derived from drill results ([PRD 14](14-non-goals.md)).

**Does it simulate the attack, or run against my real stack?**
It runs against the **deployed stack** — the real enforcement path (MCP proxy, credential broker,
confinement, compiled policy, halt), not a sandbox stand-in. agentdrill owns **no** enforcement of its own
([PRD 02](02-architecture.md)).

**What about model drift?**
Packs pin seeds and models. When a pinned model changes or dies, we re-pin and re-publish rather than
silently change a number; the re-pin cadence is an open question ([PRD 08](08-risks.md)).

**Who is it for?**
Security/platform engineers (**P2 Ravi**) running agent workloads, and ecosystem builders/embedders
(**P5 Alex**) who need their own controls regression-tested. The **public** is the audience for the
published benchmark ([PRD 04](04-users-and-cujs.md)).

**What harnesses does it support?**
Harness-agnostic by construction where possible; per-harness attack packs where a harness has a specific
configuration surface. ≥2 Tier-1 at v0.1.0 ([PRD 05](05-features.md) §Compatibility).

**Is it honest about failure?**
Yes — that is the product. Every published result includes the **misses**. A result with no misses is
suspicious, not impressive ([PRD 05](05-features.md) R5, [PRD 07](07-success-metrics.md)).

**How is it built?**
It absorbs the eval-harness mechanics of the shipped the predecessor eval harness (shipped, retired, retained privately) — scenario packs, adapter
contract, trajectory capture, deterministic + judge scoring, baselines, comparison, CI exit codes,
sandbox/trust model — re-pointed from *grading agent quality* to *proving defense effectiveness*
([PRD 02](02-architecture.md), [PRD 10](10-feature-parity.md)).
