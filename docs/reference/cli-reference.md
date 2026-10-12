# CLI Reference

**Status:** draft (design intent). Command surface for `agentdrill` v0.1.0.

> **M1 status:** the full command surface below is **registered** (`agentdrill --help` lists every
> command). Commands whose engine lands in a later milestone run as explicit *planned* stubs that fail
> loudly (reserved exit 2) rather than silently no-op.

## Commands

| Command | Purpose |
|---|---|
| `agentdrill run` | Run a pack against a target; `--target`, `--tags`, `--workers`, `--max-outstanding`, `--max-cost`, `--sandbox`, `--ci`, `--output-format`, `--dry-run`, `--explain`, `--fail-on compatibility\|enforcement\|integrity`, `--fail-on-divergence critical`, `--no-manifest`, `--full` |
| `agentdrill quickstart` | Boot the bundled demo stack and produce a first honest result (≤15 min; `demo — never evidence`) |
| `agentdrill validate` | Validate packs/targets; `--strict`, `--pre-flight` |
| `agentdrill list` | List `packs`, `cases` (`--tag/--target/--difficulty`), `oracles`, `targets`, `drivers` |
| `agentdrill pack` | `lint`, `diff <a> <b>`, `publish`, `verify`, `outdated`, `deprecate` |
| `agentdrill registry` | `sync` (read-only, signature-verified) |
| `agentdrill verify <bundle\|release>` | Offline, zero-install verification (intact / complete / honest-shaped) |
| `agentdrill benchmark` | `export` (fork→run→PR submission), `report` |
| `agentdrill coverage` | Reconcile the agentwatch inventory vs. exercised surfaces |
| `agentdrill attribute <case>` | Attribute a blocked→missed flip to its cause |
| `agentdrill watch` | Re-run affected packs on change (dev loop) |
| `agentdrill schedule` | Cadence runs for out-of-PR drift |
| `agentdrill init` | Scaffold a pack (`--template mcp-poisoning\|exfil-chain\|destructive-command\|supply-chain\|…`) |
| `agentdrill doctor` | Environment + target sanity |
| `agentdrill version` | Print version |

## v0.1.0 additions (PRD 25–42)

| Command | Purpose |
|---|---|
| `agentdrill run --tier T0\|T1\|T2 --k <n>` | Attacker strength + trial count; `Hold@k`/`ASR@k` + CI ([PRD 25](../prd/25-attacker-strength-and-pressure.md)) |
| `agentdrill search --effect <goal> [--family <f>]` | Effect-based bypass search; minimization + auto-regression ([PRD 28](../prd/28-policy-bypass-search.md)) |
| `agentdrill defense` | `add\|list\|kit\|conformance` — BYOD contract/SDK/conformance ([PRD 29](../prd/29-bring-your-own-defense.md)) |
| `agentdrill backtest <policy> --since <window>` | Replay recorded sessions vs. a candidate policy ([PRD 30](../prd/30-trace-backtest-and-shadow.md)) |
| `agentdrill shadow start\|report` | Log-only candidate alongside the enforced defense |
| `agentdrill path [--agent <id>]` | Attack-path graph + path status ([PRD 31](../prd/31-attack-path-and-blast-radius.md)) |
| `agentdrill intake [submit\|list\|compile <ref>]` | Incident-to-pack compiler ([PRD 32](../prd/32-incident-to-pack-compiler.md)) |
| `agentdrill ledger [list\|show\|export]` · `agentdrill waive` | Exposure ledger + time-boxed waivers ([PRD 33](../prd/33-exposure-ledger-and-waivers.md)) |
| `agentdrill attest [issue\|verify]` | Signed drill attestation ([PRD 34](../prd/34-drill-attestations-and-deploy-gate.md)) |
| `agentdrill roe [sign\|show]` · `abort` | Rules of engagement + global abort ([PRD 35](../prd/35-rules-of-engagement-and-safe-fire.md)) |
| `agentdrill detonate <ext>` | Detonate an unknown extension in the lab ([PRD 36](../prd/36-extension-detonation-lab.md)) |
| `agentdrill view` | Local run explorer ([PRD 40](../prd/40-trace-explorer.md)) |
| `agentdrill export` | `ci` (matrix), `sarif`, `oscal`, `ocsf`, `stix` ([PRD 38](../prd/38-security-ecosystem-integrations.md)) |
| `agentdrill list platforms\|defenses\|route-families` | Compatibility matrix, defenses, bypass families ([PRD 41](../prd/41-platform-compatibility.md)) |

## Output formats

`terminal` (default) · `json` · `markdown` · `github-actions` · `html` (self-contained, offline) ·
**SARIF 2.1.0** · **JUnit XML** · **OCSF/ECS** · **OSCAL** · **STIX 2.1** ([PRD 38](../prd/38-security-ecosystem-integrations.md)).

## Exit codes

| Code | Meaning |
|---|---|
| 0 | all cases behaved as expected |
| 1 | one or more cases missed |
| 2 | configuration error |
| 3 | oracle/judge infrastructure error |
| 4 | critical miss (a must-block enforcement case was not blocked) |
| 5 | critical divergence (deterministic vs judge) |

## Examples

```sh
agentdrill quickstart
agentdrill run --pack incidents-core --target ./stack.yaml --ci
agentdrill run --pack kill-chain --target ./stack.yaml --tags kill-time
agentdrill pack verify ./community-pack@1.2.0 --trust external
agentdrill verify ./benchmark-v0.1.0.json
```
