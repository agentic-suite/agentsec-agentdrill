"""M1 1.2 — the CLI exposes the full documented command surface."""

from __future__ import annotations

from click.testing import CliRunner

from agentdrill.cli.__main__ import main
from agentdrill.cli.exit_codes import ExitCode, resolve

REQUIRED_COMMANDS = {
    "run",
    "list",
    "validate",
    "verify",
    "quickstart",
    "pack",
    "registry",
    "watch",
    "schedule",
    "benchmark",
    "init",
    "doctor",
    "version",
}


def test_help_lists_full_command_surface() -> None:
    result = CliRunner().invoke(main, ["--help"])
    assert result.exit_code == 0
    missing = sorted(c for c in REQUIRED_COMMANDS if c not in result.output)
    assert not missing, f"--help is missing commands: {missing}"


def test_each_command_parses_help() -> None:
    runner = CliRunner()
    for cmd in sorted(REQUIRED_COMMANDS):
        result = runner.invoke(main, [cmd, "--help"])
        assert result.exit_code == 0, f"`{cmd} --help` failed: {result.output}"


def test_exit_code_precedence() -> None:
    assert resolve() == ExitCode.OK
    assert resolve(ExitCode.OK) == ExitCode.OK
    assert resolve(ExitCode.MISS, ExitCode.OK) == ExitCode.MISS
    assert resolve(ExitCode.MISS, ExitCode.CONFIG_ERROR) == ExitCode.CONFIG_ERROR
    assert resolve(ExitCode.CRITICAL_MISS, ExitCode.CONFIG_ERROR) == ExitCode.CRITICAL_MISS
    assert (
        resolve(ExitCode.CRITICAL_DIVERGENCE, ExitCode.CONFIG_ERROR) == ExitCode.CRITICAL_DIVERGENCE
    )
    assert resolve(ExitCode.ORACLE_ERROR, ExitCode.MISS) == ExitCode.ORACLE_ERROR


def test_planned_command_fails_loudly() -> None:
    result = CliRunner().invoke(main, ["pack", "publish"])
    assert result.exit_code == int(ExitCode.CONFIG_ERROR)
    assert "not yet implemented" in result.output


PLANNED_INVOCATIONS = [
    ["list", "oracles"],
    ["list", "targets"],
    ["list", "drivers"],
    ["pack", "lint"],
    ["pack", "lint", "./pack.yaml"],
    ["pack", "publish"],
    ["pack", "verify", "--trust", "external"],
    ["pack", "deprecate"],
]


def test_every_planned_command_fails_loudly() -> None:
    runner = CliRunner()
    for args in PLANNED_INVOCATIONS:
        result = runner.invoke(main, args)
        assert result.exit_code == int(ExitCode.CONFIG_ERROR), (args, result.output)
        assert "not yet implemented" in result.output, args


def test_verify_is_implemented_not_a_stub() -> None:
    """M31 31.4 / plan 4.5.8: `verify` is wired, so it fails loudly with a real
    message (never the "not yet implemented" stub)."""
    runner = CliRunner()
    no_path = runner.invoke(main, ["verify"])
    assert no_path.exit_code == int(ExitCode.CONFIG_ERROR)
    assert "requires a bundle path" in no_path.output
    assert "not yet implemented" not in no_path.output

    missing = runner.invoke(main, ["verify", "./does-not-exist.json"])
    assert missing.exit_code == int(ExitCode.CONFIG_ERROR)
    assert "bundle not found" in missing.output
    assert "not yet implemented" not in missing.output


def test_invalid_config_exits_config_error(tmp_path) -> None:
    bad = tmp_path / "agentdrill.toml"
    bad.write_text("not = = valid === toml")
    result = CliRunner().invoke(main, ["--config", str(bad), "version"])
    assert result.exit_code == int(ExitCode.CONFIG_ERROR)
    assert "configuration error" in result.output


def test_valid_config_is_accepted(tmp_path) -> None:
    good = tmp_path / "agentdrill.toml"
    good.write_text("[judge]\nprovider = 'openai'\n")
    result = CliRunner().invoke(main, ["--config", str(good), "version"])
    assert result.exit_code == 0
