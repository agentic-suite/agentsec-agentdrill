# ADR-0009 — Signed packs + enforced trust levels

- **Status:** accepted
- **Context:** external packs are executable code; a hostile or typo-squatted pack is a supply-chain risk.
- **Decision:** packs are **Sigstore-signed** with verified publishers; a `trust` level
  (`built-in`/`local`/`external`) is **enforced at load/run** (external ⇒ sandboxed subprocess only); the
  registry index is signed and content-addressed; deprecation/takedown recorded on the signature chain
  (DD-20, DD-25).
- **Consequences:** untrusted packs cannot execute with full access and never reach a benchmark release;
  registry poisoning is rejected at install.
