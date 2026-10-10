# Runbook — Tamper Response

**Goal:** when an integrity check fails on a pack, evidence bundle, or artifact, respond correctly —
**fail-closed**, never warn-and-continue.

```sh
agentdrill pack verify ./pack@1.2.0        # signature + publisher + hash
agentdrill verify ./evidence-bundle.json   # signatures, hashes, manifest, labels
agentdrill doctor                          # harness/config integrity
```

**Rules**

1. **Tamper = block.** A failed signature/hash on a pack halts the run (`--trust external` enforces
   sandbox-only regardless).
2. **Loud, not silent.** The failure names the **first broken link**; a drifted pack is quarantined.
3. **Never trust a fixed-looking number.** If a published result's hash does not match its manifest, treat
   the number as void until re-published with a re-pin note.
4. **Record + disclose.** Takedown of a registry entry is recorded on the signature chain; a security issue
   follows the org disclosure process ([SECURITY.md](../../SECURITY.md)).

**Evidence bundles** are re-verified by a third party with **nothing installed** — if theirs fails and yours
passes, diff the bundle (`agentdrill verify --explain` names the broken link).

**Related:** the evasion pack (R7) is the *sanctioned* way to attack the ecosystem; these checks are what it
proves.
