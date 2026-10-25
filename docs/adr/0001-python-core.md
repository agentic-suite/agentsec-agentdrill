# ADR-0001 — Python core, one engine across surfaces

- **Status:** accepted
- **Context:** agentdrill needs a library, a CLI, and a CI/pytest surface without divergent behavior.
- **Decision:** a single Python core (pack format, runner, driver/target adapters, oracle engine, reporter)
  with thin CLI and pytest wrappers (DD-15). `pip install agentsec-agentdrill`; CLI `agentdrill`.
- **Consequences:** one engine, three surfaces — no parallel implementations that drift. Python-first;
  other-language consumers use the CLI/JSON/HTTP surfaces.
