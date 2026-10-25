"""M29 29.3 — corpus import (RED → GREEN).

Import public human-found corpora (licence-checked) into packs/catalogue; a mapped
pack must be **lint-clean** (every case carries ATLAS + OWASP tags).
"""

from __future__ import annotations

import pytest

from agentdrill.breakit import (
    ALLOWED_LICENSES,
    CorpusEntry,
    CorpusError,
    check_license,
    import_corpus,
    require_lint_clean,
)
from agentdrill.interop.tagging import TaggingError


def _entries() -> list[CorpusEntry]:
    return [
        CorpusEntry(
            id="art-001",
            source="ART-benchmark",
            license="Apache-2.0",
            title="tool-arg injection",
            tags=["ATLAS-AML.T0051", "OWASP-A03"],
        ),
        CorpusEntry(
            id="art-002",
            source="ART-benchmark",
            license="MIT",
            title="memory poisoning",
            tags=["ATLAS-AML.T0057", "OWASP-A01"],
        ),
    ]


def test_allowed_licences_are_the_documented_oss_set() -> None:
    assert "Apache-2.0" in ALLOWED_LICENSES
    assert "MIT" in ALLOWED_LICENSES


def test_import_builds_a_lint_clean_pack() -> None:
    pack = import_corpus(_entries(), corpus_name="art-benchmark")
    assert pack.pack.name == "art-benchmark"
    assert [case.id for case in pack.cases] == ["art-001", "art-002"]
    assert all("origin:corpus" in case.tags for case in pack.cases)
    require_lint_clean(pack)


def test_a_disallowed_licence_is_refused() -> None:
    entry = CorpusEntry(id="x", source="vendor", license="Proprietary", title="x", tags=[])
    with pytest.raises(CorpusError):
        check_license(entry)
    with pytest.raises(CorpusError):
        import_corpus([entry], corpus_name="vendor")


def test_an_untagged_case_fails_the_lint() -> None:
    entry = CorpusEntry(id="y", source="ART", license="MIT", title="y", tags=["ATLAS-AML.T0051"])
    pack = import_corpus([entry], corpus_name="art")
    with pytest.raises(TaggingError):
        require_lint_clean(pack)
