# Versioning Policy

**Status:** normative (v0.1.0).

## agentdrill (the tool)

- **Semver.** MAJOR: breaking CLI/config/pack-format changes. MINOR: new commands, packs, adapters (backwards
  compatible). PATCH: fixes.
- One version across package, CLI, and CHANGELOG (enforced by a consistency test at M32).
- **Everything that can move a number is pinned in the run manifest**: pack `@version`+hash, seed(s),
  model(s), oracle `@version`, target/driver digests, **lab `@version`**, and the OTel semconv version. A change
  to any pin is a *declared* change (regex: re-pin ⇒ re-publish), never a silent one.

## Pack format

- A pack carries its own semver in **`pack.version`** (immutable once published) and a tool-compatibility
  gate in **`pack.min_agentdrill`**: a tool **refuses** a pack whose `min_agentdrill` is newer than the running
  tool (fail-closed, exit 2).
- Additive optional fields are backwards compatible (older tools ignore unknown keys). A breaking field change
  ships under a new pack **MAJOR** version with a migration note.
- v0.1.0 has **no** separate `format_version` field: `pack.version` + `pack.min_agentdrill` are the whole
  compatibility surface, and they are exactly the fields the pack schema requires.

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
