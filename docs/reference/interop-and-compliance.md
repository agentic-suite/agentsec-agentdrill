# Interop & Compliance — Reference

**Status:** normative (M17). Implementation: `src/agentdrill/interop/`. Design:
[interop](../design/interop.md). Spec: [PRD 03](../prd/03-landscape.md).

## Interop importer (17.1, F12)

`import_suite(data, tool)` → `ImportedCase[]` for `promptfoo` / `garak` / `agentdojo` / `pyrit`;
`to_pack(imported, name=, version=, target=)` → a runnable `AttackPack`. Format translation only; the
imported pack runs through the core runner unchanged.

## Standards tagging (17.2, F13)

`has_atlas` / `has_owasp` (prefixes `ATLAS-` / `OWASP-`); `untagged_cases(pack)`; `validate_tagging(pack)`
raises `TaggingError`. `registry.lint_pack` includes a `standards` check.

## Adversary profiles (17.3, F54)

`AdversaryProfile(who, what, source, objective)`; `render_profile` (Markdown card); `profile_section`
(result payload); `validate_profile` rejects an empty field.

## Compliance-mapped reporting (17.4, F24)

`FRAMEWORKS = (eu_ai_act_art12, nist_ai_rmf, iso_42001)`. `map_finding(finding_type)` → control ids;
`build_compliance_report([(case_id, finding_type)], generated=)` → `ComplianceReport`;
`export_agentcomply(report, dest)` writes `compliance-report.json`. Unknown finding type ⇒
`ComplianceError`.

## Standards submission + fuzzing (17.5, F28/R13)

`SUBMISSION_TARGETS = (nist-caisi, agentdojo-inspect, owasp-agentic)`;
`build_submission(target, pack_ref=, summary=, generated=)` + `export_submission(submission, dest)`.
`FUZZ_PACK_CLASS = "oss-fuzz"`; `fuzz_class_pack(name)` builds an OSS-Fuzz-class pack.

## Competitor benchmark (17.6, R12)

`competitor_row(stack=, pack_ref=, outcome=, seeds=)` → `CompetitorRow`; `build_table(rows)` →
`CompetitorTable`; `export_table(table, dest)`; `reproduces(expected, actual)` checks rows (numbers +
seeds) match.
