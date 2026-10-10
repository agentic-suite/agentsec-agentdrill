# agentdrill docs

Documentation for **agentdrill** — the continuous adversarial-testing (**proof**) engine for AI-agent
defenses. Part of the [agentsec-ecosystem](https://github.com/agentsec-ecosystem).

> **Status: v0.1.0 planned.** Requirements + design complete; the build is the WBS. Docs are **design
> intent** until M31–M32, then rewritten against the built system.

## Sections

| Directory / file | Purpose |
|---|---|
| [prd/](prd/) | Product requirements — why, architecture, landscape, CUJs, features, security, metrics, risks, roadmap, data model, chains, registry, kill-chain, BAS, efficacy, packs, DX, oracle credibility, gap closure, **+ world-class additions (effect witness, attacker strength, BYOD, integrations, backtest/path/intake, ledger/attestation/RoE, detonation/break-it/frontier, explorer/platform/standards) and the evidence register** (PRDs 25–43) |
| [design/](design/) | Subsystem designs + decisions + threat model |
| [reference/](reference/) | CLI, pack-format spec, adapter API, compatibility, errors, limitations, policies |
| [adr/](adr/) | Architecture Decision Records |
| [architecture/](architecture/) | Spec + component architecture (v0.1.0) |
| [wbs/](wbs/) | Work breakdown, by version (index + parts, 2 milestones per file) |
| [plans/](plans/) | Execution plans + testing/absorption strategy |
| [field-test/](field-test/) | Field-test plan + report, by version |
| [release/](release/) | Release notes, security audit, claims ledger, verifier |
| [runbooks/](runbooks/) | Operational runbooks |
| [tutorials/](tutorials/) | Hands-on guides |
| [guides/](guides/) | User guide |
| [compliance/](compliance/) | OWASP/ATLAS/NIST/EU/OpenSSF mappings |
| [examples/](examples/) · [articles/](articles/) · [skills/](skills/) | Samples, posts, the read-only drill skill |
| [`../schema/`](../schema/) | Machine-readable pack JSON Schema |

Root docs: [glossary](glossary.md) · [development](development.md) · [deployment](deployment.md) ·
[gtm](gtm.md) · [examples](examples.md) · [maintenance backlog](maintenance-backlog.md).

## Start here

- [PRD index](prd/README.md) · [Why](prd/01-why.md) · [Architecture](prd/02-architecture.md)
- [User guide](guides/user-guide.md) · [Getting started tutorial](tutorials/01-getting-started.md)
- [Runbooks](runbooks/README.md) · [Design](design/README.md) · [WBS](wbs/v0.1.0/wbs-v0.1.0-index.md)

## Conventions

- **BLUF** — Bottom Line Up Front in major documents.
- **Design intent** — pre-build docs say so; rewritten at M31–M32.
- **Honesty** — misses and limitations are documented, not hidden.
- **Versioned directories** — each documentation type is organized by version.
