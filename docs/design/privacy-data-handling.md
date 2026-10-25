# Privacy & Data Handling — Design

**BLUF:** Evidence bundles contain target internals (system prompts, config, tool schemas); local-first by
default (no egress unless configured); secrets/PII are redacted **before** bundling with verifiable
**redaction receipts**; credentials are referenced by name, never persisted (DD-05/DD-20).

> **Built (v0.1.0)** (pre-build). WBS M18/M22.

## Data classes

| Class | Example | Handling |
|---|---|---|
| Target secrets | API keys, tokens, creds | referenced by **name** only; never persisted |
| Target internals | system prompt, config, schemas | in bundles only, redacted + receipted |
| Attack content | payloads, args | part of the public pack (documented patterns) |
| Results / evidence | outcomes, agentwatch refs | local under `.agentdrill/` |
| Environment | `run-manifest.json` | **names only**, never values; `--no-manifest` to omit |

## Egress

- **Local-first:** no network for core function.
- Sharing is explicit: `agentdrill benchmark export` / evidence bundle / registry sync (read-only).
- Sandbox (`--sandbox`) strips env vars from driver processes; `external` trust packs run isolated
  (`--network none`, read-only root, resource caps).

## Evidence privacy (F65)

1. Redaction runs **before** bundling (never persist then scrub).
2. **Redaction receipts** record what class was redacted, how many, and where — the recipient sees *that*
   something was hidden, not *what*.
3. The **verifier** (F64) checks receipts against the policy, so a bundle can't smuggle content out or hide
   evidence behind bogus redactions.

## Audit integrity

The audit log is append-only, rotated, and **hash-chained**; tamper ⇒ fail-closed (closes the predecessor
flat-log gap G4).

## Disclosure

Security reports follow [SECURITY.md](../../SECURITY.md) / the org policy; the evasion pack (R7) is the
sanctioned self-attack, and unsanctioned testing follows the org disclosure process.
