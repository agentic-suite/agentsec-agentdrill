"""M1 1.5 — self-observability: doctor verdict + structured logging."""

from __future__ import annotations

import json
import logging

from click.testing import CliRunner

from agentdrill import doctor as doctor_mod
from agentdrill import logging as adlog
from agentdrill.cli.__main__ import main
from agentdrill.config import AgentDrillConfig


def test_run_checks_ok_on_clean_env() -> None:
    checks = doctor_mod.run_checks(AgentDrillConfig())
    assert checks
    assert not doctor_mod.has_failures(checks)


def test_has_failures_only_counts_critical() -> None:
    failing = [doctor_mod.Check(name="x", ok=False, detail="boom", critical=True)]
    assert doctor_mod.has_failures(failing)
    warn_only = [doctor_mod.Check(name="x", ok=False, detail="warn", critical=False)]
    assert not doctor_mod.has_failures(warn_only)


def test_doctor_cli_reports_ok_verdict() -> None:
    result = CliRunner().invoke(main, ["doctor"])
    assert result.exit_code == 0
    assert "doctor: OK" in result.output


def test_doctor_cli_reports_problems(monkeypatch) -> None:
    monkeypatch.setattr(
        doctor_mod,
        "_check_python",
        lambda: doctor_mod.Check(name="python", ok=False, detail="too old"),
    )
    result = CliRunner().invoke(main, ["doctor"])
    assert result.exit_code == 2
    assert "PROBLEMS FOUND" in result.output


def test_configure_logging_structured_json(capsys) -> None:
    logger = logging.getLogger("agentdrill")
    logger.handlers.clear()
    try:
        adlog.configure_logging(logging.INFO, structured=True)
        logger.info("hello structured")
        captured = capsys.readouterr()
        line = captured.err.strip().splitlines()[-1]
        payload = json.loads(line)
        assert payload["message"] == "hello structured"
        assert payload["level"] == "INFO"
    finally:
        logger.handlers.clear()


def test_configure_logging_text_mode(capsys) -> None:
    logger = logging.getLogger("agentdrill")
    logger.handlers.clear()
    try:
        adlog.configure_logging(logging.INFO, structured=False)
        logger.info("hello text")
        captured = capsys.readouterr()
        assert "hello text" in captured.err
    finally:
        logger.handlers.clear()
