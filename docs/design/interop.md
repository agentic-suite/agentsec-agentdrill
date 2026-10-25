# Interop, Standards & Compliance — Design

**BLUF:** Import the community's attack suites instead of reinventing them (format translation only);
tag every pack/attack with MITRE ATLAS + OWASP; emit compliance-mapped reports (EU AI Act Art. 12 /
NIST AI RMF / ISO 42001) and standards-submission artifacts; publish the competitor honest-coverage
benchmark (R9, R10, R12).

> **Status:** normative (M17). **Implementation:** `agentdrill/interop/` — `importers.py` (F12),
> `tagging.py` (F13), `profiles.py` (F54), `compliance.py` (F24), `submission.py` (F28/R13),
> `competitor.py` (R12). Reference: [interop-and-compliance](../reference/interop-and-compliance.md).
> Spec: [PRD 03](../prd/03-landscape.md).

## Interop importer (17.1, F12)

A connector layer translates promptfoo / garak / AgentDojo / PyRIT suites into attack packs
(`import_suite` → `ImportedCase` → `to_pack`). **Format translation only** — the imported pack runs
through the same core runner, unchanged.

## Standards tagging (17.2, F13)

Every case carries a `ATLAS-*` and an `OWASP-*` tag; `validate_tagging` (and the lint `standards` check)
rejects an untagged pack.

## Adversary profiles (17.3, F54)

A pack-level threat-intel card (`AdversaryProfile`: who / what / source / objective) rendered on results
(`render_profile`, `profile_section`).

## Compliance-mapped reporting (17.4, F24)

`map_finding` maps a finding type to control ids in EU AI Act Art. 12, NIST AI RMF and ISO 42001;
`build_compliance_report` + `export_agentcomply` produce an offline artifact.

## Standards submission + fuzzing (17.5, F28/R13)

`build_submission`/`export_submission` generate an artifact for NIST CAISI / AgentDojo-Inspect / OWASP
Agentic; **OSS-Fuzz** is a pack class (`fuzz_class_pack`, `FUZZ_PACK_CLASS`).

## Competitor benchmark (17.6, R12)

`CompetitorRow`/`CompetitorTable` publish third-party honest-coverage rows via the PR-submission path;
`reproduces` checks a row's numbers and seeds.
