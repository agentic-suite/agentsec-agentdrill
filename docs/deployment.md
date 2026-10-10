# Deployment

**Status:** design intent.

## Local-first (default)

agentdrill runs on the developer machine with no service: packs, runner, oracles, and reporter are local;
artifacts land under `.agentdrill/`; nothing egresses unless configured.

```sh
agentdrill quickstart                        # bundled demo
agentdrill run --pack incidents-core --target ./stack.yaml --sandbox
```

## CI

- **Per commit:** deterministic oracles + fixtures, no API keys ([tutorial 03](tutorials/03-run-in-ci.md)).
- **Nightly / pre-release:** full pack + judge.
- **Untrusted packs:** `--trust external` restricts adapters to sandboxed subprocess; Docker with
  `--network none`, read-only root, resource caps.

## Targets

The deployed stack components are configured per target: `agentgate`, `agentkeys`, `agentseatbelt`/
`agentkernel`, `policyweave-output`, `agenthalt`; evidence read from **agentwatch**.

## Supply chain

Signed artifacts + SBOM + provenance on release; `agentdrill verify` checks a bundle offline.

## Settings (intended)

| Key | Meaning |
|---|---|
| `AGENTDRILL_HOME` | artifact root (default `.agentdrill/`) |
| `AGENTDRILL_TARGET` | default target config path |
| `AGENTDRILL_NO_MANIFEST` | suppress the run manifest (privacy-sensitive) |
