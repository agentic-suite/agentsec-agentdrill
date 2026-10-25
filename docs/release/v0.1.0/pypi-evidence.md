# PyPI Evidence — v0.1.0

**Status:** ✅ **published** 2026-10-25 (WBS M32, work item 32.10). The package is live and verified.

## Published

| Item | Value |
|---|---|
| Package | [`agentsec-agentdrill`](https://pypi.org/project/agentsec-agentdrill/) |
| Version | **0.1.0** |
| Release page | <https://pypi.org/project/agentsec-agentdrill/0.1.0/> |
| Files | `agentsec_agentdrill-0.1.0-py3-none-any.whl`, `agentsec_agentdrill-0.1.0.tar.gz` |
| Upload tool | `twine` (token auth via a GitHub Actions secret for CI; see below) |

## Verification (clean environment)

| Check | Result |
|---|---|
| `pip install agentsec-agentdrill==0.1.0` in a fresh Python 3.11 venv | ✅ installed |
| `agentdrill version` | ✅ **0.1.0** (matches the release) |
| `agentdrill doctor` | ✅ OK |
| Published wheel SHA-256 vs `dist/SHA256SUMS` | ✅ match (`62c9da960971fdfe…`) |
| Sdist SHA-256 vs `dist/SHA256SUMS` | ✅ match (`48cfe67f25ac3dc9…`) |

Reproduce:

```sh
uv venv /tmp/verify && uv pip install --python /tmp/verify/bin/python agentsec-agentdrill==0.1.0
/tmp/verify/bin/agentdrill version   # -> 0.1.0
python3 -c "import json,urllib.request; d=json.load(urllib.request.urlopen('https://pypi.org/pypi/agentsec-agentdrill/0.1.0/json')); [print(u['filename'], u['digests']['sha256'][:16]) for u in d['urls']]"
```

## CI publishing

The tag-triggered [`release.yml`](../../../.github/workflows/release.yml) `publish-pypi` job publishes from the
signed build. It authenticates with the **`PYPI_API_TOKEN` repository secret** (set 2026-10-25); trusted
publishing (OIDC) remains an option once the `pypi` environment + PyPI trusted publisher are configured.

> **Secret hygiene.** The v0.1.0 token was provided out of band and is stored only as an encrypted Actions
> secret (never in the repo). It should be **rotated** and the secret updated, per the standard leak-response
> rule.

Related: [release-evidence.md](release-evidence.md) (SBOM, checksums, provenance, SLSA target) ·
[release-notes.md](release-notes.md).
