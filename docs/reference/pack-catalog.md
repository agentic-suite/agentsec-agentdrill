# Pack Catalog — v0.1.0

**Status:** normative (M2). The packs ship in [`packs/`](../../packs/); fixtures in
[`packs/fixtures/`](../../packs/fixtures/). Format: [pack-format-spec.md](pack-format-spec.md).

The launch catalog is four packs, 21 cases. Every case carries an `incident_ref` and ATLAS + OWASP coverage
tags; the catalog is discoverable with `agentdrill list packs` / `agentdrill list cases`.

| Pack | Cases | Theme |
|---|---|---|
| [`quickstart-demo`](../../packs/quickstart-demo.yaml) | 5 | Bundled demo — shows the honest-reporting shape (a green, a miss **by design**, a kill-time case, a seam, a benign twin) |
| [`incidents-core`](../../packs/incidents-core.yaml) | 6 | Documented core incidents re-pointed from the launch families: Replit destructive command, policy-argument binding, boundary denial, budget enforcement, fail-closed recovery, coding-agent regression |
| [`incidents-security`](../../packs/incidents-security.yaml) | 8 | Prompt-injection override, system-prompt extraction, Slack-AI exfil chain, credential encode-to-log, SSRF metadata probe, sandbox-escape traversal, MCP tool poisoning, Plugin4Shell supply chain |
| [`kill-chain`](../../packs/kill-chain.yaml) | 2 | Kill-time across the full chain, and the highest-severity revoked-but-still-acting cease gap |

## Using the catalog

```sh
agentdrill validate --pack packs/incidents-core.yaml --strict
agentdrill list packs
agentdrill list cases --tag exfiltration
agentdrill list cases --target agentseatbelt --difficulty hard
```

## Not yet in this catalog

The remaining PRD 21 packs — `evasion-self-attack` (M14), `efficacy-control` (M13), `meta-verification`
(M23) — land with their milestones. A class in the roadmap but not shipped shows as `untested` in the
heat-map (F53) — never silently omitted.

> The catalog is data, not evidence: the demo pack is watermarked `demo` and `mock`-attested. Published
> numbers bind to `pack@version+hash` (DD-28).
