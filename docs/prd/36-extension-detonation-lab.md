# PRD 36 — Extension Detonation Lab

**BLUF:** The extension surface exploded (>10,000 published MCP servers; 60,000+ AGENTS.md projects; plugins/skills/hooks/rules everywhere) and it is where documented attacks live (Plugin4Shell, tool poisoning up to 72.8% ASR, rug-pulls, Amazon Q wiper prompt, rules-file backdoors). Static scanners miss runtime behavior, conditional payloads, and post-approval drift. Add a **dynamic detonation** mode: run an unknown extension in the hermetic lab with canaries/sinks and a driver agent, and produce a cited **Behavior Report** with honesty labels and a version **diff** (rug-pull watch).

**Status:** Draft — v0.1.0 addition (2026-10-10) · **Owner:** @deghosal-2026 · **Parent:** agentic-suite #209 · **Features:** F98 · **Reqs:** R72

## Why

- Software supply chain solved the equivalent with dynamic detonation (VirusTotal, ANY.RUN, Socket-class behavior analysis); **nobody offers it for agent extensions**.
- Static scanners read metadata/code and miss conditional/sleeper behavior and post-approval change.
- agentdrill already owns the pieces (hermetic lab, canaries, witnesses, driver agent) — detonation is high-value reuse and also provides "behavior truth" for scanner conformance ([PRD 29](29-bring-your-own-defense.md)).

## Requirements (v0.1.0)

| # | Requirement | Acceptance criterion |
|---|---|---|
| **R72** | A **detonation** mode runs unknown extensions (MCP servers, skills, plugins/hooks, rules files, packages) in the hermetic lab, observes behavior via [PRD 26](26-independent-effect-witness.md) witnesses, and emits a cited Behavior Report with honesty labels and per-version diff. | Seeded-malicious recall ≥ 80% (≥ 90% target); precision ≥ 85%; zero lab escapes / real-network contact. |

## Features

| # | Feature | Req | Notes |
|---|---|---|---|
| **F98** | **Extension detonation lab**: extension types (MCP server stdio/HTTP; skill `SKILL.md` + scripts/resources; plugin/hook; rules/instruction file; agent template; package that registers tools) · observed signals (egress/DNS, honey-file reads, out-of-scope writes, process spawn, metadata drift, conditional behavior, agent-directed injection content, declared-vs-actual mismatch) · Behavior Report with per-ATLAS/ASI tags, policy suggestions, prior-version diff · optional signed attestation (F96) | R72 | Consumes [PRD 27](27-adversary-lab.md)/[PRD 26](26-independent-effect-witness.md)/[PRD 35](35-rules-of-engagement-and-safe-fire.md); feeds F19 supply-chain class |

### Honesty
Reports state **conditions covered / not covered** ("observed within N runs over T minutes under driver D; absence of evidence ≠ safe"). Sleepers/sandbox-detection are expected → multi-schedule runs (time-shifted, repeated, varied personas) reported as coverage, never "clean."

## CUJs

### CUJ-50 — Before allowlisting
Detonate a new MCP server before allowlisting; report shows an outbound POST to an unlisted domain on the 3rd call. **Success:** evidence + policy suggestion (egress allowlist).

### CUJ-51 — Registry admission
A new version is detonated; metadata drift vs. the previous version is flagged. **Success:** flagged before publish.

## Success metrics

| Metric | Target |
|---|---|
| Recall on seeded malicious behaviors (exfil, cred theft, rug-pull, conditional, escape) | ≥ 80% (v0.1.0); ≥ 90% target |
| Precision (reviewer-confirmed ÷ flagged) | ≥ 85% |
| Benign-extension false-flag rate (top-100 popular benign extensions) | ≤ 5% |
| Detonation wall time per extension (default profile) | ≤ 10 min p95 |
| Rug-pull detection when swap occurs after approval/N calls | ≥ 95% (seeded) |
| Sandbox-evasion detection on seeded set | ≥ 70% |
| Reports carrying explicit "conditions covered / not covered" | 100% |
| Lab escapes / real-network contact | **0** |
| Detonation true positives vs. static scanners on same corpus | ≥ +20% (measure) |

## Dependencies
F19, F59, F63 · [PRD 26](26-independent-effect-witness.md), [PRD 27](27-adversary-lab.md), [PRD 35](35-rules-of-engagement-and-safe-fire.md), [PRD 34](34-drill-attestations-and-deploy-gate.md).

## Boundaries & non-goals
- **Never "safe":** a clean report is bounded evidence.
- Dual-use: running malware-like code → strict isolation (VM/microVM), RoE, no real egress; OSS-first (don't detonate code whose license forbids analysis without consent).
- Scope limited to *agent extension* behavior — not an AV/EDR.

## Open questions
1. Seeded-corpus provenance (documented incidents only + dual-use review).
2. Publish a public "extension behavior" feed (vendor right-of-reply per [PRD 29](29-bring-your-own-defense.md))?
