"""Logging configuration for AgentDrill library consumers.

Usage:
    import logging
    logging.getLogger("agentdrill").setLevel(logging.INFO)

AgentDrill modules log via ``logging.getLogger("agentdrill.<module>")``.

Logger hierarchy::
    agentdrill               - root package logger (WARNING by default)
    agentdrill.scoring       - scoring engine operations
    agentdrill.cache         - cache hits, misses, corruptions
    agentdrill.security      - sandbox, audit, policy enforcement
    agentdrill.runner        - scenario runner lifecycle
    agentdrill.loading       - pack YAML/JSON loading and validation
"""

from __future__ import annotations

import logging


def configure_logging(level: int = logging.WARNING) -> None:
    """Configure the agentdrill logger with a basic handler if none exists."""
    logger = logging.getLogger("agentdrill")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        ))
        logger.addHandler(handler)
    logger.setLevel(level)
