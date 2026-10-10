# ADR-0002 — Attack packs as YAML with strict validation

- **Status:** proposed
- **Context:** packs are executable security claims that must be reviewable, versioned, and safe to load.
- **Decision:** versioned **YAML** packs (`pack` + `cases[]`, JSON secondary), strictly validated:
  duplicate-id, missing-field, incoherent-budget, oracle/target/driver resolution, threshold ranges, and
  **path-safe identifiers** (`^[a-zA-Z0-9_-]+$`) before any path use (DD-16).
- **Consequences:** packs are diffable and reviewable like code; the strict validator closes the
  predecessor's traversal gap at the foundation (G3). Unknown references fail loudly, never silently.
