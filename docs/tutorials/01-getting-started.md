# Tutorial 01 — Getting Started

**You'll get:** a first honest drill result in ≤15 minutes, and the mental model.

## 1. Install

```sh
# Install (PyPI) — first release: v0.1.0
pip install agentsec-agentdrill==0.1.0
agentdrill --help
# Verify the download (optional): compare the wheel hash with the release SHA256SUMS;
# SBOM + provenance: docs/release/v0.1.0/release-evidence.md
```

## 2. First run (no real stack needed)

```sh
agentdrill quickstart
```

You'll see a **blocked** case, a deliberate **miss** (so you see the honest-reporting shape), a kill-chain
timeline, and an exportable evidence bundle — all watermarked `demo — never evidence`.

## 3. Point at your stack

```sh
agentdrill validate --pack incidents-core --strict
agentdrill run --pack incidents-core --target ./my-stack.yaml --sandbox
```

The result is `blocked` / `missed` / `degraded`, with the agentwatch evidence behind each case.

## 4. The mental model

- A **pack** is a versioned replay of documented incidents.
- A **driver** delivers the attack; a **target** is your deployed enforcement.
- An **oracle** decides blocked/missed/degraded (deterministic first).
- **Efficacy** proves the attack lands unguarded; **kill-time** proves cessation.

## Next

- Author your own pack → [02 — Write an attack pack](02-write-an-attack-pack.md)
- Gate a PR → [03 — Run in CI](03-run-in-ci.md)
