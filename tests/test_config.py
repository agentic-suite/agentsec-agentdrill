"""Tests for agentdrill.config (project config loading)."""

from __future__ import annotations

from pathlib import Path

from agentdrill import config


def test_defaults_when_no_file(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("AGENTDRILL_CONFIG", raising=False)
    cfg = config.load_config()
    assert cfg.judge_provider == "openai"
    assert cfg.judge_model == "gpt-4o-mini"
    assert cfg.output_dir == ".agentdrill"
    assert cfg.log_level == "info"
    assert cfg.strict_mode is False
    assert cfg.compare_mode == "snapshot"
    assert cfg.raw == {}


def test_find_config_explicit_file(tmp_path: Path) -> None:
    f = tmp_path / "agentdrill.toml"
    f.write_text("[judge]\n")
    assert config._find_config_file(f) == f


def test_find_config_explicit_dir(tmp_path: Path) -> None:
    f = tmp_path / "agentdrill.toml"
    f.write_text("")
    assert config._find_config_file(tmp_path) == f


def test_find_config_explicit_missing(tmp_path: Path) -> None:
    assert config._find_config_file(tmp_path / "nope.toml") is None


def test_find_config_env_var(tmp_path: Path, monkeypatch) -> None:
    f = tmp_path / "agentdrill.toml"
    f.write_text("")
    monkeypatch.setenv("AGENTDRILL_CONFIG", str(f))
    assert config._find_config_file() == f


def test_find_config_env_var_missing(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("AGENTDRILL_CONFIG", str(tmp_path / "nope.toml"))
    assert config._find_config_file() is None


def test_find_config_cwd(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("AGENTDRILL_CONFIG", raising=False)
    monkeypatch.chdir(tmp_path)
    assert config._find_config_file() is None
    (tmp_path / "agentdrill.toml").write_text("")
    assert config._find_config_file() == tmp_path / "agentdrill.toml"


def test_load_config_values(tmp_path: Path) -> None:
    f = tmp_path / "agentdrill.toml"
    f.write_text(
        "[judge]\n"
        "provider = 'anthropic'\n"
        "model = 'claude-3'\n"
        "[output]\n"
        "dir = 'out'\n"
        "log_level = 'debug'\n"
        "[scoring]\n"
        "strict = true\n"
        "compare_mode = 'rescore'\n"
    )
    cfg = config.load_config(f)
    assert cfg.judge_provider == "anthropic"
    assert cfg.judge_model == "claude-3"
    assert cfg.output_dir == "out"
    assert cfg.log_level == "debug"
    assert cfg.strict_mode is True
    assert cfg.compare_mode == "rescore"
    assert "judge" in cfg.raw


def test_load_config_invalid_toml(tmp_path: Path) -> None:
    f = tmp_path / "agentdrill.toml"
    f.write_text("this = = not valid === toml")
    cfg = config.load_config(f)
    assert cfg == config.AgentDrillConfig()


def test_load_config_tomllib_unavailable(tmp_path: Path, monkeypatch) -> None:
    f = tmp_path / "agentdrill.toml"
    f.write_text("[judge]\n")
    monkeypatch.setattr(config, "tomllib", None)
    cfg = config.load_config(f)
    assert cfg == config.AgentDrillConfig()
