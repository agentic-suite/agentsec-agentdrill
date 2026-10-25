"""M32 32.6 — one version across package/CLI/CHANGELOG, and a policy that matches
the code.

RED before the policy fix: the versioning policy documented ``pack.format_version``,
which nothing implements. The last test catches that class of drift.
"""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

from click.testing import CliRunner

from agentdrill import __version__
from agentdrill.cli.__main__ import main

REPO = Path(__file__).resolve().parents[1]


def _pyproject() -> dict:
    return tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))


def test_package_version_matches_pyproject() -> None:
    assert __version__ == _pyproject()["project"]["version"]


def test_cli_version_matches_package() -> None:
    result = CliRunner().invoke(main, ["version"])
    assert result.exit_code == 0
    assert result.output.strip() == __version__


def test_changelog_has_no_other_version() -> None:
    """Every released version heading must equal the package version."""
    text = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    headings = re.findall(r"^## \[(.+?)\]", text, flags=re.MULTILINE)
    assert headings, "CHANGELOG must have at least an [Unreleased] heading"
    released = [h for h in headings if h.lower() != "unreleased"]
    assert all(h == __version__ for h in released), headings


def test_pack_schema_gates_tool_compatibility() -> None:
    schema = json.loads((REPO / "schema" / "pack.schema.json").read_text(encoding="utf-8"))
    required = schema["properties"]["pack"]["required"]
    assert "min_agentdrill" in required
    assert "version" in required


def test_run_envelope_schema_version_is_pinned() -> None:
    schema = json.loads((REPO / "schema" / "run-envelope.schema.json").read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == "agentdrill.run_envelope.v1"


def test_versioning_policy_only_documents_real_pack_fields() -> None:
    """The policy must not name pack fields that do not exist (no phantom drift)."""
    policy = (REPO / "docs" / "reference" / "versioning-policy.md").read_text(encoding="utf-8")
    schema = json.loads((REPO / "schema" / "pack.schema.json").read_text(encoding="utf-8"))
    real = set(schema["properties"]["pack"]["properties"].keys())
    documented = set(re.findall(r"pack\.([a-z_]+)", policy))
    phantom = sorted(documented - real)
    assert not phantom, f"versioning-policy documents non-existent pack field(s): {phantom}"


def test_versioning_policy_is_released_not_draft() -> None:
    policy = (REPO / "docs" / "reference" / "versioning-policy.md").read_text(encoding="utf-8")
    assert "**Status:** draft" not in policy
