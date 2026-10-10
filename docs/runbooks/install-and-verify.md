# Runbook — Install & Verify

**Goal:** a first honest result in ≤15 minutes, and confidence the install is sound.

```sh
# 1. Install
pip install agentsec-agentdrill
agentdrill --help

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
