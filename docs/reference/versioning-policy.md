# Versioning Policy

**Status:** draft (design intent).

## agentdrill (the tool)

- **Semver.** MAJOR: breaking CLI/config/pack-format changes. MINOR: new commands, packs, adapters (backwards
  compatible). PATCH: fixes.
- One version across package, CLI, and CHANGELOG (enforced by a consistency test at M24).

## Pack format

- **`pack.format_version`** is independent of the tool version and evolves under its own policy:
  - MINOR: additive optional fields (older tools ignore unknown fields).
  - MAJOR: breaking field changes (older tools reject; a migration path is published).
- `pack.min_agentdrill` gates tool compatibility; a tool **refuses** a pack whose format it does not support.

## Packs (registry)

- Packs are **semver'd and immutable** once published (`pack@version` + hash). A fix is a new version.
- **Deprecation** is explicit with migration notes; deprecated packs keep running but are flagged and
  excluded from new benchmark releases.
- **Re-pin rule** (DD-18/DD-28): when a pinned model/seed changes, results are **re-published** with a note;
  numbers never change silently.

## Oracle versioning (F79)

- Oracles are semver'd and pinned in the manifest. An oracle MAJOR that changes verdict semantics
  **invalidates comparability** → a re-baseline note publishes with the next release.

## Compatibility table

Each release publishes the harness × version compatibility table ([compatibility.md](compatibility.md)).
