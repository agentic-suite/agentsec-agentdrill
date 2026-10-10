# Data Dictionary

**BLUF:** The entities agentdrill reads and writes: **AttackPack → AttackCase → Target/Driver → Run →
Result → Finding → Evidence**, with Coverage tags, goldens, comparisons, and the published BenchmarkRelease.
Stored locally under `.agentdrill/`; machine-consumed results use the **agentwatch schema**.

> **Design intent** (pre-build). The normative pack schema is [pack-format.md](pack-format.md).

## Entities

| Entity | Definition | Key fields |
|---|---|---|
| **AttackPack** | Versioned curated set of attack cases | `name`, `version`, `description`, `min_agentdrill`, `license`, `trust`, `hash` |
| **AttackCase** | One attack step bound to a target + oracle | `id`, `title`, `goal`, `incident_ref`, `target`, `driver`, `attack`, `oracle`, `benign_twin`, `cleanup`, `tags`, `difficulty`, `budget` |
| **Target** | A deployed-stack component | `type` (`agentgate`/`agentkeys`/`agentseatbelt`/`agentkernel`/`policyweave-output`/`agenthalt`), `config`, `attestation` |
| **Driver** | How an attack is delivered | `type` (`subprocess`/`python`/`http`/`claude-code`/`cursor`), `config`, `digest` |
| **Run** | One execution of a pack | `run_id`, `pack`(+hash), `target`, `driver`, `manifest`, timestamps |
| **Result** | Per-case outcome | `case_id`, `outcome` (`blocked`/`missed`/`degraded`), `dimensions`, `exit_code` |
| **Finding** | A miss/degradation worth surfacing | `case_id`, `type` (taxonomy), `severity`, `evidence_refs`, `attributed_to` |
| **Evidence** | agentwatch events tied to a result | event refs (`denied`, `policy-fired`, `revoked`, `halted`, `secret-detected`) |
| **CoverageTag** | Standards mapping | `atlas[]`, `owasp_llm[]`, `owasp_agentic[]` |
| **GoldenResult** | Accepted expected outcome | `case_id`, `expected_outcome`, `pack_version` |
| **Comparison** | Candidate vs. golden diff | per-case/tag/aggregate deltas; change flags |
| **BenchmarkRelease** | Published per-release table | `release`, `results[]`, `kill_time[]`, `manifest_ref` |
| **DefenseContract** | Required pack an enforcer ships | `tool`, `pack_ref`, `min_pass` |
| **KillChainTimeline** | Per-case stage timestamps | `attack_start`…`ceased` (each nullable + flagged) |
| **ReconSnapshot** | Target's exposed surface at run time | `tools[]`, `mcp_servers[]`, `capabilities[]`, `case_bindings` |
| **EfficacyStatus** | Whether a case succeeds unguarded | `case_id`, `unguarded_outcome` (`succeeded`/`inert`) |
| **Attestation** | Target's realness level | `component`, `level` (`live`/`fixture`/`mock`) |
| **Severity** | attack-class × exposure | `class`, `exposure`, `score`, `rationale` |
| **AdaptiveProvenance** | Parent pattern for an adaptive case | `parent_pattern`, `mutation_summary`, `reviewer` |
| **ReviewVerdict** | HITL decision on a divergence | `case_id`, `verdict`, `reviewer`, `seed_corpus_ref` |
| **RegistryEntry** | Published pack in the registry | `pack@version`, `signature`, `publisher`, `changelog`, `deprecated` |

## `.agentdrill/` layout

```
.agentdrill/
  packs/            # resolved/imported packs (by name + version)
  runs/<run_id>/    # run.json, run-manifest.json, artifacts/<case_id>.json, recon.json
  goldens/          # golden expected results per pack version
  comparisons/      # candidate vs. golden/baseline diffs
  benchmarks/       # published BenchmarkRelease tables
  audit/            # append-only, rotated, hash-chained policy/trust log
```

## Invariants

No ground-truth leakage · case independence · reproducibility (manifest+hash) · honesty (full outcome
split) · evidence binding · surface honesty · adaptive provenance · mechanism-backed attribution ·
path-safe identifiers (`^[a-zA-Z0-9_-]+$`) · kill-chain gaps flagged never inferred.
