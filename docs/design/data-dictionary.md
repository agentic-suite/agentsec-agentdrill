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
| **EffectDeclaration** | Effects a case must prevent / preserve (M23) | `forbidden[]`, `preserved[]` |
| **Witness** | Independent effect observation (M23) | `kind` (`fs`/`net`/`cred`/`proc`/`ledger`/`surface`), `observation`, `hash_chain_ref`, `live` |
| **LabService** | Adversary-lab counterparty (M23) | `kind` (mcp/idp/registry/api/a2a/sink), `version`, `events[]` (ground truth) |
| **AttackerTier** | Attacker strength + effort (M24) | `tier` (T0–T3), `k`, `mutation_path`, `seed`, `hold_at_k`, `asr_at_k`, `pressure_curve` |
| **RouteFamily** | Catalogued bypass family (M24) | `effect`, `family`, `coverage` (`tried`/`blocked`/`bypassed`/`untried`) |
| **Bypass** | A confirmed bypass + minimal repro (M24) | `family`, `reproducer`, `attributed_to`, `regression_ref` |
| **Defense** | A drillable defense via the contract (M25) | `decision_points`, `config_digest`, `fail_mode`, `version`, `tos_notes`, `conformance_level` |
| **AttackPath** | Reachability path (M27) | `source`, `target_asset`, `hops[]`, `severity`, `status` (`proven_broken`/`open_missed`/`unproven`/`accepted`) |
| **FindingStatus** | Ledger lifecycle (M28) | `state` (`open`…`verified_fixed`/`decayed`/`accepted_risk`/`false_positive`/`wont_fix`), `owner`, `due` |
| **Waiver** | Time-boxed risk acceptance (M28) | `scope`, `tier`, `reason`, `compensating_control`, `approvers`, `expires`, `residual_risk`, `signature` |
| **DrillAttestation** | Signed proof of a drill (M28) | in-toto predicate `agentdrill/drill-result/v1`, `subject` (config digest), `predicate`, `signature`, `issued`, `expires` |
| **BehaviorReport** | Extension detonation result (M29) | `extension`, `observations[]`, `conditions_covered`, `diff_vs_prior`, `tags[]` |

## `.agentdrill/` layout

```
.agentdrill/
  packs/            # resolved/imported packs (by name + version)
  runs/<run_id>/    # run.json, run-manifest.json, artifacts/<case_id>.json, recon.json
  goldens/          # golden expected results per pack version
  comparisons/      # candidate vs. golden/baseline diffs
  benchmarks/       # published BenchmarkRelease tables
  audit/            # append-only, rotated, hash-chained policy/trust log
  witness/          # per-case witness records + hash chain (M23)
  lab/              # pinned adversary-lab definitions (M23)
  bypass/           # confirmed bypass families + minimized reproducers (M24)
  waivers/          # signed time-boxed waivers (M28)
  attestations/     # signed drill attestations (M28)
```

## Invariants

No ground-truth leakage · case independence · reproducibility (manifest+hash) · honesty (full outcome
split) · evidence binding · surface honesty · adaptive provenance · mechanism-backed attribution ·
path-safe identifiers (`^[a-zA-Z0-9_-]+$`) · kill-chain gaps flagged never inferred ·
**effects adjudicated by witnesses outside the defended stack** (M23) · **every number carries attacker
tier + `Hold@k` + CI** (M24) · **canary-only destructive effects; signed RoE** (M28) · **waivers annotate,
never relabel** (M28).
