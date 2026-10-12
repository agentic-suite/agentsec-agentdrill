"""Logging configuration for AgentDrill library consumers.

Usage:
    import logging
    from agentdrill.logging import configure_logging
    configure_logging(logging.INFO, structured=True)

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

import json
import logging

_TEXT_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


class JsonFormatter(logging.Formatter):
    """Structured logging: one JSON object per record."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "time": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(payload)


def configure_logging(level: int = logging.WARNING, *, structured: bool = False) -> None:
    """Configure the ``agentdrill`` logger.

    Adds a stream handler if none exists, sets the formatter (JSON when
    ``structured`` is true, else a human-readable line), and sets the level.
    Safe to call repeatedly: it never adds a second handler.
    """
    logger = logging.getLogger("agentdrill")
    if not logger.handlers:
        logger.addHandler(logging.StreamHandler())

    formatter: logging.Formatter = (
        JsonFormatter() if structured else logging.Formatter(_TEXT_FORMAT)
    )
    for handler in logger.handlers:
        handler.setFormatter(formatter)
    logger.setLevel(level)
