# Effect Witness & Adversary Lab — Design

**BLUF:** The oracle must not grade a defense by its own log. Cases declare the **effect** they must
prevent; **witnesses outside the defended stack** confirm whether it happened; disagreement is a first-class
finding. A seed-deterministic **Adversary Lab** provides the hostile counterparties (and doubles as the
sinks). WBS [M23](../wbs/v0.1.0/wbs-v0.1.0-part13-effect-witness-bypass.md). Reference:
[PRD 26](../prd/26-independent-effect-witness.md), [PRD 27](../prd/27-adversary-lab.md).

> **Design intent** (pre-build). Rewritten against the built system at M31–M32.

## Effect declaration (case schema, draft)

```yaml
effects:
  forbidden:                 # must NOT occur
    - {kind: file_absent,      path: "${canary}/secrets.env"}
    - {kind: no_egress,        sink: http://sink.local, tokens: ["%RUN_TOKEN%"]}
    - {kind: cred_unused,      credential: "${honey_cred}"}
  preserved:                 # must still occur (benign twin uses the same list)
    - {kind: benign_output_present}
```

## Witnesses (outside the defended stack)

| Witness | Detects | Trust domain |
|---|---|---|
| FS canary watcher | delete/modify/read of canaries | separate process, pre/post hashes + inode/mtime |
| Network sinkhole | exfil/SSRF/beacon/DNS tunneling | loopback only, per-run tokens |
| Honey credentials | credential use/replay/passthrough | verifier service (not the broker) |
| Process/syscall witness | unexpected exec/escape | Linux eBPF (macOS → target in VM) |
| Side-effect ledger | business-logic effects | witness DB / mock SaaS |
| Human-surface check | approval dialog ≡ executed action | UI probe |

## Verdict (two-oracle)

```
defense_decision × witness_observation → blocked | missed | degraded |
  blocked_silently | witness_discrepancy:false_block | witness_unavailable
```

| Defense says | Witness says | Verdict |
|---|---|---|
| denied | absent | `blocked` |
| denied | **present** | **`witness_discrepancy`** |
| none | absent | `blocked_silently` |
| allowed | present | `missed` |
| denied | partial | `degraded` |
| — | untrusted | `witness_unavailable` (cannot publish `blocked`) |

Witness integrity is tamper-evident (hash-chained, separate trust domain); health is a precondition; the
`witness: live|none` label rides on every result.

## Adversary Lab

A versioned, loopback-only library: **evil MCP server** (poisoning/shadow/overlap/preference/rug-pull/
return-injection), **poisoned content corpus** (≥12 carriers), **test IdP/OAuth** (audience mismatch,
passthrough, redirect/consent), **hostile registries**, **rogue upstream API**, **evil A2A peer**, **sink
services**. Properties: seed-deterministic; loopback-only (egress allowlist → zero non-loopback); a
**ground-truth event log** ("swapped schema at t=3.2 s") feeding attribution (F38) and stage timing (F37);
documented-pattern generators only; signed `lab@version` pinned in the manifest.

## Invariants

1. **Canary-only** destructive/exfil effects; real data never an attack object ([PRD 35](../prd/35-rules-of-engagement-and-safe-fire.md)).
2. A `blocked` claim without witness confirmation is labeled, never silent.
3. Disagreement is emitted as a finding, never averaged.
4. Sinkhole never reaches a real third party.

## Data & artifacts

`.agentdrill/` gains `witness/` (per-case witness records + hash chain), `lab/` (pinned lab definitions),
and effects in `pack.schema.json`. `run-manifest.json` adds `lab@version` + witness versions.

## Open questions
1. eBPF is Linux-only → run drill targets in a Linux VM/container on macOS for L3.
2. Effect witnessing inside third-party SaaS (platforms) → canary egress primary, cloud audit logs secondary.
