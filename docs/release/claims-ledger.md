# Claims Ledger

Every public claim agentdrill makes, with the artifact that evidences it. A claimed-but-unevidenced row is a
release blocker (org governance floor). Design intent; populated as evidence lands.

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
| C-12 | Untrusted packs cannot execute unsandboxed | sandbox + trust enforcement test | planned |

> **Rule:** no claim ships without its evidence artifact; the ledger is the release gate's checklist.
