# Claims Ledger

Every public claim agentdrill makes, with the artifact that evidences it. A claimed-but-unevidenced row is a
release blocker (org governance floor). Built (v0.1.0); populated as evidence lands.

| # | Claim | Evidence | Status |
|---|---|---|---|
| C-1 | Packs replay documented incidents faithfully | pack `incident_ref` + source citations + fit test | planned |
| C-2 | Runs exercise the **deployed** stack | target attestation (`live`) + evidence refs | planned |
| C-3 | The CI gate rejects un-blocking policy changes | `gate-a-policy-pr` field scenario + meta exit-code case | planned |
| C-4 | Published numbers are reproducible by a third party | reproduction run + `verify` verdict (runbook) | planned |
| C-5 | Every published number includes its misses | reporter honesty gate (no-misses fails publish) | planned |
| C-6 | Numbers are multi-seed with CIs | statistics publish check (single-run rejected) | planned |
| C-7 | Enforcement is efficacy-backed | unguarded twin run; `attack_inert` exclusions | planned |
| C-8 | Kill-time measures cessation | cessation probe (re-attempt) + timeline | planned |
| C-9 | The ecosystem self-attacks every release | evasion pack + dark holdout cadence | planned |
| C-10 | Results are independently verifiable offline | standalone verifier (three verdicts) | planned |
| C-11 | Oracles are credible, not drifting | calibration corpus + judge-drift canary | planned |
| C-12 | A `blocked` claim rests on an **observed effect**, not the defense's log | independent witness + `witness_discrepancy` handling ([PRD 26](../prd/26-independent-effect-witness.md)) | planned |
| C-13 | Every published number states **attacker strength + `Hold@k` + CI** | tier/k/CIs on every cell; pressure curve ([PRD 25](../prd/25-attacker-strength-and-pressure.md)) | planned |
| C-14 | Rule-green implies effect-safe over catalogued bypass routes | route-family search coverage; auto-regressions ([PRD 28](../prd/28-policy-bypass-search.md)) | planned |
| C-15 | Head-to-heads are **neutral** (no composite score/ranking) | pre-registration + right-of-reply + config-digest cells ([PRD 29](../prd/29-bring-your-own-defense.md)) | planned |
| C-16 | Findings reach buyer tooling | SARIF/OTel/OCSF/OSCAL/STIX schema-valid in CI ([PRD 38](../prd/38-security-ecosystem-integrations.md)) | planned |
| C-17 | Waivers never relabel a miss (visibility preserved) | signed waivers; misses remain in all reports ([PRD 33](../prd/33-exposure-ledger-and-waivers.md)) | planned |
| C-18 | A deploy gate can consume a fresh, signed proof | in-toto `agentdrill/drill-result/v1` + Sigstore + freshness ([PRD 34](../prd/34-drill-attestations-and-deploy-gate.md)) | planned |
| C-19 | Drills never touch out-of-scope targets/bystanders | signed RoE + fail-closed preflight + canary-only + abort ([PRD 35](../prd/35-rules-of-engagement-and-safe-fire.md)) | planned |
| C-20 | Standards coverage incl. OWASP ASI 2026 is declared with gaps | ASI table with `untested`; claims linter green ([PRD 42](../prd/42-standards-and-claims.md)) | planned |
| C-12 | Untrusted packs cannot execute unsandboxed | sandbox + trust enforcement test | planned |

> **Rule:** no claim ships without its evidence artifact; the ledger is the release gate's checklist.
