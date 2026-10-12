"""Tests for agentdrill.logging."""

from __future__ import annotations

import logging

from agentdrill import logging as adlog


def test_configure_logging_adds_handler_once_and_sets_level() -> None:
    logger = logging.getLogger("agentdrill")
    logger.handlers.clear()
    try:
        adlog.configure_logging(logging.INFO)
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1
        # A second call must not add another handler, but must update the level.
        adlog.configure_logging(logging.DEBUG)
        assert len(logger.handlers) == 1
        assert logger.level == logging.DEBUG
    finally:
        logger.handlers.clear()
