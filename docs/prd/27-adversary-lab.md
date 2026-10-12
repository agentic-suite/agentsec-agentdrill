# PRD 27 — Adversary Lab (Hostile-Environment Kit)

**BLUF:** Real incidents require an **attacker-controlled counterparty** — a poisoned web page, an inbox, an MCP server that changes behavior after approval, a typosquat registry, a rogue upstream API. Fixtures/ToolStub (F5) are static and cannot express time-dependent, conditional, or stateful hostile behavior. The Adversary Lab is a **versioned, loopback-only, seed-deterministic library of hostile services and content generators** that any pack can use — and that doubles as the sink/witness layer for [PRD 26](26-independent-effect-witness.md).

**Status:** Draft — v0.1.0 addition (2026-10-10) · **Owner:** @deghosal-2026 · **Parent:** agentic-suite #209 · **Features:** F88 · **Reqs:** R62

## Why

- Packs currently depend on per-author bespoke servers, harming fidelity and reviewability (PRD 17 review criteria depend on faithfulness).
- Rug-pulls, conditional/sleeper payloads, OAuth flows, and content-carrier attacks (hidden text in HTML/CSS/PDF/images) are **not representable** with static fixtures.
- MCP benchmark suites (MCPSecBench "playground", AgentDojo environments) ship reusable environments; our packs need the same to match their fidelity.

## Requirements (v0.1.0)

| # | Requirement | Acceptance criterion |
|---|---|---|
| **R62** | A reusable **Adversary Lab** provides documented-pattern hostile services and content generators, deterministic by seed, isolated to loopback, and emitting a ground-truth event log. | ≥ 70% of documented MCP attack types reproducible; same seed ⇒ same lab event log (≥ 99.9%); zero non-loopback egress. |

## Features

| # | Feature | Req | Notes |
|---|---|---|---|
| **F88** | **Adversary Lab**: evil MCP server (poisoning, shadowing/overlap, preference manipulation, rug-pull after approval/N calls/time, return-value injection) · poisoned content corpus (web, HTML/CSS-hidden, markdown, PDF, DOCX, spreadsheet, image, email, calendar, GitHub issues/PRs/README, chat) · test IdP/OAuth server (audience mismatch, token passthrough, redirect confusion, consent bypass, DCR vs Client-ID-metadata) · hostile registries (npm/PyPI/MCP/skill lookalikes, typosquat, version-swap) · rogue upstream API · evil A2A peer · sink services (HTTP/DNS/SMTP/TCP) | R62 | Consumes/serves [PRD 26](26-independent-effect-witness.md); feeds [PRD 32](32-incident-to-pack-compiler.md) |

### Properties (non-negotiable)
1. **Deterministic by seed**; behavior schedule is part of the manifest → replayable.
2. **Loopback/isolated only**; never reachable from the internet; never targets third-party hosts.
3. **Ground-truth event log** ("swapped tool schema at t=3.2s") → attribution (F38) and stage timing (F37).
4. **Documented-pattern generators only** — no new exploit techniques (PRD 14).
5. **Versioned and signed** like packs (F39); packs pin `lab@version`.

## CUJs

### CUJ-32 — Author a rug-pull case quickly
"Approve tool v1, swap description after the 3rd call." **Success:** authorable in ≤ 30 min; the lab records the swap event as ground truth.

### CUJ-33 — Carrier matrix
The same injection payload through 12 carriers. **Success:** the report shows which carriers the defense missed.

## Success metrics

| Metric | Target |
|---|---|
| Documented MCP attack types reproducible (vs. MCPSecBench 17 / MCP-SafetyBench 20) | ≥ 80% / ≥ 70% |
| Indirect-injection carrier formats | ≥ 12 |
| Pack cases using lab services vs. bespoke fixtures | ≥ 70% of MCP/injection cases |
| Replay determinism (same seed ⇒ same lab event log) | ≥ 99.9% |
| Time to author a new hostile-counterparty case (median, trained author) | ≤ 30 min |
| Lab network-egress violations (non-loopback) | **0** |
| Lab services with a ground-truth event log | 100% |

## Dependencies
F5, F19, F20, F39 · [PRD 26](26-independent-effect-witness.md), [PRD 35](35-rules-of-engagement-and-safe-fire.md).

## Boundaries & non-goals
- The Lab is the closest thing to an "arsenal": **documented-pattern generators only**, maintainer-reviewed; a published boundary doc per DD-34.
- Not a general-purpose pentest framework; scoped to agent-relevant counterparties.

## Open questions
1. Build vs. wrap MCPSecBench/AgentDojo environments (license-compatible wrap preferred).
2. Publish the Lab standalone for other tools? (Recommend: yes — standards participation.)
