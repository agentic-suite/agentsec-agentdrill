# Contributing

Thanks for helping make agent defenses provable. agentdrill is part of the
[agentic-suite](https://github.com/agentic-suite); the org
[CONTRIBUTING](https://github.com/agentic-suite/.github/blob/main/CONTRIBUTING.md) and
[GOVERNANCE](https://github.com/agentic-suite/.github/blob/main/GOVERNANCE.md) apply.

## Ground rules

- **Honesty is the product.** Never weaken a miss to make a result look better; a green with no misses is
  suspicious, not impressive.
- **No new scope outside the non-goals** ([docs/prd/14-non-goals.md](docs/prd/14-non-goals.md)): no detection
  claims, no enforcement, no novel-capability development, no proprietary scoring.
- **Packs are executable security claims** — they are reviewed like code.

## Workflow

1. One change at a time: write the test first (RED → GREEN).
2. Keep the diff scoped to the linked WBS item.
3. At milestone end (not between tickets): full suite, coverage ≥95%, `ruff`, `mypy --strict`.
4. **Definition of done:** implemented + tests passing + committed + pushed + tracking issue closed.

## Commits

Conventional commits, signed off (`git commit -s`, DCO).

## Packs

Author with `agentdrill init --template …`; `agentdrill pack lint` must pass (schema, `incident_ref`,
oracle, tags, twins, cleanup). New packs need an independent reviewer.

## Security

Report vulnerabilities per [SECURITY.md](SECURITY.md) — never a public issue.

## License

By contributing you agree your contribution is licensed under [Apache-2.0](LICENSE).
