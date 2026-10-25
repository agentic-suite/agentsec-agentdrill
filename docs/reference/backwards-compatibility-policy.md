# Backwards-Compatibility Policy

**Status:** built (v0.1.0).

## Guarantees

| Surface | Guarantee |
|---|---|
| CLI commands/flags | additive within a MAJOR; removals go through a deprecation cycle |
| Config keys | additive; deprecated keys warn for one MINOR before removal |
| Pack format | additive optional fields within a format MINOR; breaking changes bump the format MAJOR |
| Run artifacts (`run.json`, `run-manifest.json`, `artifacts/*.json`) | readers tolerate unknown fields; a schema version is stamped |
| `agentdrill.run_envelope.v1` | stable within v1; a v2 is a new `schema_version` |
| agentwatch schema consumption | we **consume** it, never fork it; a schema change is tracked, not absorbed silently |

## Deprecation cycle

1. **Announce** (release notes) — the surface is deprecated, replacement named.
2. **Warn** for at least one MINOR (CLI warning / config warning).
3. **Remove** at the next MAJOR, with a migration note.

## Pack-format evolution

- MINOR: new optional fields; older tools ignore them (forward-compatible).
- MAJOR: breaking; older tools **reject** with a clear `PackParseError`; a migration path is published.

## Reproducibility guarantee

Published results bind to `pack@version+hash` + manifest. A compatibility change never retroactively alters
a published number; a changed number is re-published with a note (golden-lock, DD-28).

## What is *not* guaranteed

- Experimental surfaces (prefixed/documented) may change without the cycle.
- `experimental` oracles are advisory and cannot gate CI (F84).
