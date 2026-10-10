# Testing & Absorption Strategy

**BLUF:** agentdrill's tests enforce **honesty** structurally: a run without misses can't publish, a
single-seed number is rejected, an inert attack can't pad a green table, and a `mock`-attested result can't
be evidence. Tests are organized in the same layers agentwatch uses, plus an **absorption/parity suite**
that gates the predecessor's capabilities.

## Test layers

| Layer | Covers | Gate |
|---|---|---|
| **Unit** | models, loader/validator, oracles, adapters, comparison, kill-chain, efficacy | coverage ≥95% |
| **Contract** | driver/target adapter contract; **ground-truth-leakage guard**; envelope/fallback | per driver |
| **Determinism** | fixtures record/replay ⇒ identical scores; manifest completeness; pin-change detection | reproduction |
| **Integration** | a pack runs end to end; evidence bound; CI exit codes; reporter formats | per milestone |
| **Meta-verification** | drill-the-drill against our own oracles (vacuous pass, exit code, fixtures intercept) | CI, every cycle |
| **Evasion** | self-attack pack fails closed; dark holdout catches pack-gaming | release cycle |
| **Field** | CUJ-1..24 end to end against a real deployed stack (M23) | field-test report |

## Honesty gates (structural, not aspirational)

- No-misses publish → **fails**.
- Single-seed / bare-percentage number → **fails**.
- Inert (`attack_inert`) case counted as coverage → **fails**.
- `mock`-attested result published → **fails**.
- Cleanup failure (`dirty_target`) → **release-blocking**.
- Undeclared pin/oracle change → **fails** (golden-lock).

## Absorption / parity suite (PRD 10 + PRD 24)

An executable gate (M21) asserting every absorbed capability is **delivered + tested / delegated / waived**
and every predecessor gap **G1–G14** is closed with a test or waived with a reason. It fails CI on drift —
no capability or gap silently drops.

## Gates & cadence

- **Per ticket:** the ticket's test RED → GREEN. No full suite between tickets.
- **Per milestone end:** full suite · coverage ≥95% · `ruff` · `mypy --strict` — run once.
- **CI:** fast path (deterministic + fixtures, no keys) per commit; full + judge nightly / pre-release.
- **Release (M24):** full suite + absorption gate + first-run timed test + release-tooling verification.

## Coverage target

**≥95%** across the suite, enforced in CI (the predecessor's standard, carried forward).
