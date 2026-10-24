"""M18 18.7 — quickstart + demo stack, F66 (RED → GREEN).

`agentdrill quickstart` boots a bundled demo target and reaches a first honest
result in ≤15 minutes — mock-attested and watermarked `demo — never evidence`.
"""

from __future__ import annotations

from click.testing import CliRunner

from agentdrill.cli.__main__ import main
from agentdrill.lifecycle import (
    BUDGET_MINUTES,
    DEMO_WATERMARK,
    QuickstartResult,
    run_quickstart,
    within_budget,
)


def test_quickstart_reaches_a_first_result() -> None:
    result = run_quickstart()
    assert isinstance(result, QuickstartResult)
    assert result.outcome.total > 0


def test_quickstart_is_mock_attested_and_watermarked() -> None:
    result = run_quickstart()
    assert result.attestation == "mock"
    assert "never evidence" in result.watermark
    assert DEMO_WATERMARK == result.watermark


def test_quickstart_is_within_budget() -> None:
    result = run_quickstart()
    assert within_budget(result) is True
    assert BUDGET_MINUTES == 15
    assert result.elapsed_seconds <= BUDGET_MINUTES * 60


def test_quickstart_cli_exits_cleanly() -> None:
    result = CliRunner().invoke(main, ["quickstart"])
    assert result.exit_code == 0, result.output
    assert "never evidence" in result.output
