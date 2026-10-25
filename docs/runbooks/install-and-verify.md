# Runbook — Install & Verify

**Goal:** a first honest result in ≤15 minutes, and confidence the install is sound.

```sh
# 1. Install (PyPI) — first release: v0.1.0
pip install agentsec-agentdrill==0.1.0
agentdrill --help

# 1b. Verify the download (optional, offline): hash + SBOM + build attestation
pip download agentsec-agentdrill==0.1.0 -d ./dl --no-deps
shasum -a 256 ./dl/*.whl            # compare against the release SHA256SUMS
#   SBOM (CycloneDX) + SHA256SUMS + signed provenance:
#   docs/release/v0.1.0/release-evidence.md
#   PyPI: https://pypi.org/project/agentsec-agentdrill/

# 2. Sanity
agentdrill doctor

# 3. First run against the bundled demo stack (offline, synthetic)
agentdrill quickstart          # → blocked/missed + kill-chain timeline + evidence bundle
                               #   watermarked "demo — never evidence"

# 4. Point at your own deployed stack
agentdrill validate --pack incidents-core --strict
agentdrill run --pack incidents-core --target ./my-stack.yaml --sandbox
```

**Expected:** `quickstart` shows an honest outcome split (including a deliberate miss) in minutes; the
demo bundle opens offline. The first real run reports `blocked`/`missed`/`degraded` with agentwatch
evidence and, for kill-chain cases, a stage timeline.

**Verify the install is real (not a mock):** results carry an **attestation** label — `live`, `fixture`, or
`mock`. A `mock`-attested result never publishes; if you see `mock` on a real stack run, the target config
is wrong ([design/adapter-contract](../design/adapter-contract.md)).
