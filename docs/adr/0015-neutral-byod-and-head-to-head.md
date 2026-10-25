# ADR-0015 — Neutral BYOD; head-to-heads carry no composite score or ranking

- **Status:** accepted (2026-10-10)
- **Context:** Drilling only the ecosystem's own stack reads as a vendor benchmark. Market consolidation
  (Promptfoo→OpenAI; Lakera→Check Point; Protect AI→Palo Alto; CalypsoAI→F5; Robust Intelligence→Cisco —
  **verify each**) makes an independent proof layer scarce and valuable; vendor red-team tools have explicit
  blind spots (e.g., computer-use/connected agents unsupported).
- **Decision:** An open **Defense Contract + SDK + conformance kit** lets any defense be drilled and
  compared, with OSS-first reference adapters (Defense Zoo). Head-to-heads follow published **neutrality
  rules**: pre-registration, vendor right-of-reply (14 d, raw bundle), licensed/own-configuration only,
  conflict disclosure, config-digest on every cell, default-vs-tuned labeled — and **no composite score or
  ranking**. agentdrill's own defenses are held to the same contract ([PRD 29](../prd/29-bring-your-own-defense.md)).
- **Consequences:** neutrality becomes the moat; legal/ToS review required before publishing competitor
  comparisons (DD-45); maintenance shifts to a conformance kit + community adapters rather than maintained
  connectors for everyone.
