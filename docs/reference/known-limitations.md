# Known Limitations

**Status:** draft (design intent). Honest "what this does NOT test" — shipped with every release (F34,
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

## Operational

- The **standalone verifier** proves artifact integrity and honest shape — it does not re-run the drill.
- `mock`-attested results are authoring aids, **never evidence**; they do not publish.
- Field-test coverage (M23) states explicitly what was **not** tested.
