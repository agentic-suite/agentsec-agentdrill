# Runbook — Upgrade & Rollback

**Goal:** upgrade agentdrill or a pack version without corrupting comparability.

```sh
agentdrill version
agentdrill pack outdated                 # vs the signed registry index
agentdrill registry sync                 # read-only, signature-verified
pip install -U agentsec-agentdrill
```

**Rules**

1. **Pin packs** like dependencies; upgrading a pack is a new `pack@version` (immutable once published).
2. **Comparability:** a pack minor/MINOR format change is additive; a format MAJOR rejects older tools with
   a clear error and publishes a migration path ([versioning-policy](../reference/versioning-policy.md)).
3. **Oracle/tool change:** an oracle MAJOR that changes verdict semantics **invalidates comparability** — a
   re-baseline note publishes with the next release (golden-lock).
4. **Never silently re-baseline:** a published number is never retroactively changed; a changed number is
   re-published with a note.

**Rollback**

```sh
pip install agentsec-agentdrill==<previous>
agentdrill run --pack <previous-pack@version> --target ./stack.yaml
```

**Deprecation:** deprecated packs keep running, flagged, but are excluded from new benchmark releases; the
deprecation + migration note is recorded on the signature chain.
