# agentdrill M0 — Port Execution Plan

**Spec:** [WBS M0](../wbs/v0.1.0/wbs-v0.1.0-part1-port-foundation.md#milestone-m0--port-the-predecessor-codebase) ·
[PRD 10](../prd/10-feature-parity.md) (absorption) · [PRD 03](../prd/03-landscape.md) · issues #—.

**Source:** the predecessor eval harness (MIT), **retired and retained privately** (never deleted). The port
is a bulk move; later milestones re-point the mechanics.

## Decisions

- **Workspace:** in place on the feature branch (no worktree).
- **History:** single import commit; provenance recorded in `THIRD_PARTY_NOTICES.md` + `CHANGELOG.md` (no
  `filter-repo`, no subtree). Ruling D2.
- **Namespace:** predecessor package → `agentdrill`.

## Global constraints

- **Do not clobber** agentdrill's own `docs/` (prd/design/reference/wbs/plans), `schema/`, `.github/` — they
  are ahead of the source. Port the source **code + tooling**, plus only the non-colliding source docs subset.
- **Exit gate:** ported suite green; coverage ≥ 95%; `ruff` zero; `mypy --strict` clean.
- **Commits:** conventional commits, signed off (`git commit -s`, DCO).

---

## Task 1 — Import the source tree + record provenance (0.1, 0.3, 0.6)
Copy the predecessor's `src/ tests/ scenarios/` + packaging/tooling (merged), plus the non-colliding docs
subset; skip agentdrill-owned dirs. Record provenance (source + commit + date + MIT) in `THIRD_PARTY_NOTICES`
and a `CHANGELOG [Unreleased]` entry. Commit.
**Expected:** `git ls-files` contains the ported tree; provenance includes the SHA; `git status` clean.

## Task 2 — Rename namespace → `agentdrill` (0.2)
Rename the package dir + every reference across code/tests/configs/docs. Repo-wide grep shows only the port
notes. Commit.
**Expected:** `agentdrill` package dir exists; no predecessor namespace dir.

## Task 3 — Adapt packaging metadata (0.4)
Update `pyproject.toml` `name`/description/URLs → `agentdrill` / `agentsec-agentdrill`; wire the
`agentdrill` console script. Editable install succeeds. Commit.

## Task 4 — Get the ported test suite green (0.5)
Install dev deps; run the ported suite; fix only rename-induced breakage (no behavior changes). Commit.
**Expected:** ported suite passes.

## Task 5 — Guard test: no stray predecessor references (0.T)
**RED** → write a test scanning tracked text files for the predecessor namespace (allowlisting the port
notes) and watch it fail on an un-allowlisted reference → **GREEN** → commit.
**Expected:** guard fails on a stray reference; passes on the clean tree.

## Task 6 — Update design docs (0.7, 0.D)
Describe the ported layout; update provenance/CHANGELOG; link from the WBS index + this plan. Commit.

---

## Rulings (recorded here so they survive compaction)

- **D1 — Docs collisions:** keep agentdrill's `docs/{prd,design,reference,wbs,plans}`, `schema/`, `.github/`;
  port only the non-colliding source docs subset. *Why:* agentdrill docs are the normative, newer set.
- **D2 — History:** single import commit with recorded SHA. *Why:* provenance over line-level blame across
  the port boundary.
- **D3 — Namespace scope:** "zero predecessor references" means zero **except** the port notes in
  `THIRD_PARTY_NOTICES`/`CHANGELOG` (provenance requires naming the source).
