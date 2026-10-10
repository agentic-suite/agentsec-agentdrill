"""Command-line interface for AgentDrill.

Public package entry point. The actual command implementations live in
`agentdrill.cli.__main__` to keep the package namespace clean: `__init__.py`
only re-exports the Click group `main` that the console script
(`agentdrill = "agentdrill.cli:main"` in pyproject.toml) resolves to.

Keeping the implementation in `__main__.py` (rather than inline here) means
`python -m agentdrill.cli` also works and avoids import-order pitfalls between
the console-script wrapper and package-internal imports.
"""

from agentdrill.cli.__main__ import main

__all__ = ["main"]
