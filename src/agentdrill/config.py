"""Project configuration loaded from ``agentdrill.toml``.

Config is read from an explicit path, else ``$AGENTDRILL_CONFIG``, else
``./agentdrill.toml``. Precedence is explicit path > env var > cwd. When no file
is found, defaults apply; when a file is present it is **fail-closed** — an
unparseable file, a wrong type, or (in strict mode) an unknown section/key
raises :class:`ConfigError` rather than silently defaulting.

Usage:
    from agentdrill.config import load_config
    cfg = load_config()
    print(cfg.judge_provider, cfg.judge_model)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentdrill.models.errors import ConfigError

try:
    import tomllib
except ImportError:  # pragma: no cover - py<3.11 fallback
    try:
        import tomli as tomllib  # type: ignore[no-redef]
    except ImportError:
        tomllib = None  # type: ignore[assignment]

_KNOWN_KEYS: dict[str, set[str]] = {
    "judge": {"provider", "model"},
    "output": {"dir", "log_level"},
    "scoring": {"strict", "compare_mode"},
}
_LOG_LEVELS = {"debug", "info", "warning", "error"}
_COMPARE_MODES = {"snapshot", "rescore"}


@dataclass
class AgentDrillConfig:
    """Configuration loaded from ``agentdrill.toml``."""

    # Judge defaults
    judge_provider: str = "openai"
    judge_model: str = "gpt-4o-mini"

    # Output
    output_dir: str = ".agentdrill"
    log_level: str = "info"

    # Scoring
    strict_mode: bool = False
    compare_mode: str = "snapshot"  # snapshot | rescore

    # Raw TOML data (for sub-command use)
    raw: dict[str, Any] = field(default_factory=dict)


def _find_config_file(path: str | Path | None = None) -> Path | None:
    if path:
        p = Path(path)
        if p.is_file():
            return p
        if p.is_dir():
            p = p / "agentdrill.toml"
        return p if p.is_file() else None

    env_path = os.environ.get("AGENTDRILL_CONFIG")
    if env_path:
        p = Path(env_path)
        return p if p.is_file() else None

    cwd = Path.cwd() / "agentdrill.toml"
    return cwd if cwd.is_file() else None


def _get_str(section: str, data: dict[str, Any], key: str, default: str, source: Path) -> str:
    value = data.get(key, default)
    if not isinstance(value, str):
        raise ConfigError(f"[{section}] {key} must be a string in {source}")
    return value


def _get_bool(section: str, data: dict[str, Any], key: str, default: bool, source: Path) -> bool:
    value = data.get(key, default)
    if not isinstance(value, bool):
        raise ConfigError(f"[{section}] {key} must be a boolean in {source}")
    return value


def _validate(data: dict[str, Any], source: Path, strict: bool) -> None:
    for section, section_data in data.items():
        if section not in _KNOWN_KEYS:
            if strict:
                raise ConfigError(f"unknown config section [{section}] in {source}")
            continue
        if not isinstance(section_data, dict):
            raise ConfigError(f"config section [{section}] must be a table in {source}")
        if strict:
            unknown = set(section_data) - _KNOWN_KEYS[section]
            if unknown:
                raise ConfigError(
                    f"unknown keys in [{section}]: {sorted(unknown)} in {source}"
                )


def load_config(path: str | Path | None = None, *, strict: bool | None = None) -> AgentDrillConfig:
    """Load configuration, **fail-closed** on invalid input.

    Args:
        path: Explicit config path (file or directory); overrides env/cwd.
        strict: Override the config's own ``strict`` validation (unknown
            sections/keys become errors).

    Returns:
        The parsed :class:`AgentDrillConfig`, or defaults when no file exists.

    Raises:
        ConfigError: If a config file is present but unparseable, has a wrong
            type, or (in strict mode) has an unknown section/key.
    """
    config_file = _find_config_file(path)
    if config_file is None:
        if path is not None:
            raise ConfigError(f"config file not found: {path}")
        return AgentDrillConfig()
    if tomllib is None:
        raise ConfigError("no TOML parser available (Python <3.11 without 'tomli')")

    try:
        data = tomllib.loads(config_file.read_text())
    except Exception as exc:
        raise ConfigError(f"invalid config {config_file}: {exc}") from exc
    if not isinstance(data, dict):  # pragma: no cover - tomllib always yields a table
        raise ConfigError(f"invalid config {config_file}: top level must be a table")

    scoring_cfg = data.get("scoring", {})
    if not isinstance(scoring_cfg, dict):
        raise ConfigError(f"config section [scoring] must be a table in {config_file}")
    declared_strict = _get_bool("scoring", scoring_cfg, "strict", False, config_file)
    effective_strict = declared_strict if strict is None else strict

    _validate(data, config_file, effective_strict)

    judge_cfg = data.get("judge", {})
    output_cfg = data.get("output", {})

    log_level = _get_str("output", output_cfg, "log_level", "info", config_file)
    if log_level not in _LOG_LEVELS:
        raise ConfigError(
            f"invalid log_level '{log_level}' in {config_file} "
            f"(expected one of {sorted(_LOG_LEVELS)})"
        )
    compare_mode = _get_str("scoring", scoring_cfg, "compare_mode", "snapshot", config_file)
    if compare_mode not in _COMPARE_MODES:
        raise ConfigError(
            f"invalid compare_mode '{compare_mode}' in {config_file} "
            f"(expected one of {sorted(_COMPARE_MODES)})"
        )

    return AgentDrillConfig(
        judge_provider=_get_str("judge", judge_cfg, "provider", "openai", config_file),
        judge_model=_get_str("judge", judge_cfg, "model", "gpt-4o-mini", config_file),
        output_dir=_get_str("output", output_cfg, "dir", ".agentdrill", config_file),
        log_level=log_level,
        strict_mode=effective_strict,
        compare_mode=compare_mode,
        raw=dict(data),
    )
