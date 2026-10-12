# PRD 06 — Security Baseline

**BLUF:** agentdrill's job is to attack other software, so it must be the most honest and hardened thing in
the stack. Its assets are the pack catalog, the evidence it produces, and the trust in its numbers. Its
**own attack surface** — tampering, hook-disabling, policy editing, telemetry injection — is not a footnote
but a **shipped pack** (the evasion pack, R7). Running **untrusted community packs** inherits the predecessor's
sandbox / trust-policy / audit / secret-sanitization model.

**Status:** Draft — v0.1.0 (2026-10-09) · **Owner:** @deghosal-2026 · **Parent:** agentic-suite #209

## Assets

| Asset | Why it matters |
|---|---|
| Pack catalog | Executable security claims; tampering changes what "blocked" means |
| Evidence + results | The reproducibility claim; forged results destroy the moat |
| Published benchmark | The trust artifact the whole ecosystem points at |
| Driver/target credentials | Drills touch real enforcers and (brokered) credentials |
| The recount/harness itself | If compromised, the attacker owns the proof |

## Controls

- **Determinism + manifest** (R6): pinned seeds/models/pack-hash + `run-manifest.json` make results
  reproducible and tamper-evident ([PRD 13](13-non-functional-requirements.md)).
- **Signed packs + provenance** (governance floor): pack contributions reviewed like code; signed releases.
- **Honest reporting is enforced** (R5): a run cannot publish without its misses.
- **Fail-closed on tamper** for the harness's own config/hooks (mirrors the ecosystem own-threat-model).
- **Sensitive-data handling:** credentials referenced by name only, never persisted; artifacts sanitized
  (absorbed from the predecessor harness: key-name filtering + regex deep-redaction).

## agentdrill's own attack surface (the evasion pack, R7)

Operationalized directly from the ecosystem's own threat model — the surface/threat/mitigation table
lives in [PRD 06](06-security-baseline.md) and the ecosystem threat-model design doc:

| Surface | Threat | Drill (attack) + expected defense |
|---|---|---|
| Pack catalog | Tamper a pack so a blocked attack reads as blocked-but-isn't | Signature/version check; tamper → fail-closed |
| Hooks/adapters | Attacker edits driver config to silently skip a pack | Hook/config integrity checked; tamper → loud fail |
| Policy/compiled output | Edit compiled policy to always-allow | Drill detects the un-blocked attack (CUJ-2) |
| Telemetry/evidence | Inject into telemetry so a miss reads as a block | Treat telemetry as untrusted input; no eval/dynamic render |
| Update channel | Malicious update re-runs a hostile pack set | Signed, pinned updates; update is itself a policy decision |
| Results store | Edit a published number | Manifest/hash binding; re-run reproduces or disputes |
| The agent under test | Instructed to disable/evade security tooling | Enforcement outside the agent's control plane; attempted evasion = high-severity finding |

Anti-tamper principles (from the own-threat-model): enforcement lives **outside** the agent's control
plane; **fail-closed** on integrity failure; **assume the harness is compromised**; **separation of
duties** between what holds secrets, decides, and observes.

## Running untrusted packs (absorbed from the predecessor harness)

Community packs are **executable**, so they get the predecessor's security model:

- **Sandbox mode** — strip environment variables (allowlist `PATH`, `HOME`, `TMPDIR`, `USER`, `AGENTDRILL_*`),
  filesystem isolation, optional Docker network isolation (`--network none`).
- **Trust levels** — `built-in` / `local` / `external`; external restricts adapters to sandboxed subprocess
  only and validates the pack against a strict schema (fixes the predecessor's `scenario_id` path-traversal
  gap with a strict `^[a-zA-Z0-9_-]+$` pattern before any path use).
- **Audit trail** — per-run append-only log of policy/trust decisions.
- **Secret sanitization** — deep redaction in artifacts and logs.
- **OS-level isolation** for maximum-untested packs: cgroups / Docker / Firejail (the predecessor flagged
  env-only sandboxing as insufficient for third-party code).

## Disclosure

Security problems are reported privately — see [SECURITY.md](../../SECURITY.md) (and the
[organization security policy](https://github.com/agentic-suite/.github/blob/main/SECURITY.md)).
Do not open public issues for security problems. The evasion pack is the *sanctioned* way to attack the
ecosystem; unsanctioned testing follows the org disclosure process.
