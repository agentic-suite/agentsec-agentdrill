"""M19 19.1 — oracle versioning + release notes, F79 (RED → GREEN).

Every oracle is semver'd and pinned in the manifest; a major version change
invalidates comparability (a re-baseline note). Comparison flags an oracle
version change.
"""

from __future__ import annotations

from agentdrill.credibility import (
    OracleVersion,
    major_changed,
    parse_semver,
    pin_versions,
    rebaseline_note,
    version_changed,
)


def test_oracle_is_versioned_and_pinned() -> None:
    versions = [
        OracleVersion(name="deny", version="2.1.0", behavior_notes="stricter deny events"),
        OracleVersion(name="grounding", version="1.0.0"),
    ]
    assert pin_versions(versions) == {"deny": "2.1.0", "grounding": "1.0.0"}


def test_a_version_change_is_flagged() -> None:
    changed = version_changed({"deny": "2.1.0"}, {"deny": "2.2.0"})
    assert changed == ["deny"]


def test_a_major_change_invalidates_comparability() -> None:
    assert major_changed("2.1.0", "3.0.0") is True
    note = rebaseline_note("deny", "2.1.0", "3.0.0")
    assert note is not None
    assert "re-baseline" in note


def test_a_minor_change_is_compatible() -> None:
    assert major_changed("2.1.0", "2.2.0") is False
    assert rebaseline_note("deny", "2.1.0", "2.2.0") is None


def test_semver_parsing() -> None:
    assert parse_semver("2.1.0") == (2, 1, 0)
