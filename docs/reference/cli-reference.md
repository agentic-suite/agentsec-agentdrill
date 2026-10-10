# CLI Reference

**Status:** draft (design intent). Command surface for `agentdrill` v0.1.0.

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

## Output formats

`terminal` (default) · `json` · `markdown` · `github-actions` · `html` (self-contained, offline).

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
