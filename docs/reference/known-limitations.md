# Known Limitations

**Status:** built (v0.1.0). Honest "what this does NOT test" — shipped with every release (F34,
DD-31). This is the standing list; each release's limitations register is the release-scoped version.

## By design (non-goals, [PRD 14](../prd/14-non-goals.md))

- agentdrill **replays documented incident patterns**; it does **not** develop novel model-attacking
  capability, and does not publish new exploits.
- It **measures enforcement controls**, not detection — no injection-detection claims from drill results.
- It **owns no enforcement**; it drills the deployed stack.
- No **proprietary scoring** — public methodology only.

## Coverage limits (honest)

- Packs are **as good as their oracles**: a case with a weak oracle over- or under-states coverage.
- The published benchmark covers the **shipped** and **contributed** pack classes; classes not yet shipped
  appear as `untested` in the heat-map (never omitted).
- **Model-dependent cases** are subject to pinned-model drift; the re-pin cadence is a deferred decision
  (DD-33).
- **Contamination** may affect judge-based outcomes; contaminated cases are flagged, not removed.
- Tier-1 **Copilot** coverage is via a lower layer where hooks are closed — stated as such, not claimed whole.
- Adaptive orchestration is **bounded** (mutation of documented patterns); it does not explore novel space.

## v0.1.0 additions (honest)

- **Attacker strength is bounded.** Published numbers are T0/T1/T2 only; **T3 (adaptive search) is deferred**
  ([DD-44](../design/design-decisions.md)) and, when introduced, is local-only and unpublished. A "held"
  result is not a robustness claim ([PRD 25](../prd/25-attacker-strength-and-pressure.md)).
- **Witness coverage is not total.** Some cases rely on defense telemetry alone; those are labeled
  `witness: none` and are weaker evidence ([PRD 26](../prd/26-independent-effect-witness.md)).
- **Bypass coverage is a catalogue, not a proof.** Route-family search covers catalogued families
  (≥90% of P0 effects); unsampled routes are shown `untried` ([PRD 28](../prd/28-policy-bypass-search.md)).
- **Reachability ≠ exploitability.** Attack-path status is `unproven` until a drill proves it
  ([PRD 31](../prd/31-attack-path-and-blast-radius.md)).
- **Backtest fidelity is a model of reality**; non-deterministic/stateful tools reduce it, and un-replayable
  sessions are itemized ([PRD 30](../prd/30-trace-backtest-and-shadow.md)).
- **Detonation is bounded evidence.** A clean extension report means "no adverse behavior observed under the
  conditions tried"; it is never a safety claim ([PRD 36](../prd/36-extension-detonation-lab.md)).
- **Attestations prove what was drilled, not security.** Scope, tier, witness coverage and exclusions are
  always shown; `mock`/`fixture` attestations are non-evidence ([PRD 34](../prd/34-drill-attestations-and-deploy-gate.md)).
- **No composite security score** — per-finding CVSS v4.0 + AIVSS vectors only, never aggregated
  ([PRD 42](../prd/42-standards-and-claims.md), DD-41).
- **Compliance mappings are evidence, not conformity** — every index lists what is **not** evidenced.

## Operational

- The **standalone verifier** proves artifact integrity and honest shape — it does not re-run the drill.
- `mock`-attested results are authoring aids, **never evidence**; they do not publish.
- Field-test coverage (M31) states explicitly what was **not** tested.
