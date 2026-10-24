"""Corpus import (M29 29.3, F99).

Import public, human-found corpora (e.g. the ART benchmark) into runnable packs
and the catalogue — **licence-checked** (OSS/CC only) and **lint-clean** (every
case carries ATLAS + OWASP tags, via M17's tagging SSOT). Design:
``docs/design/detonation-breakit-frontier.md``; PRD 37 (R73).
"""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel, Field

from agentdrill.interop.tagging import validate_tagging
from agentdrill.models.attack_pack import AttackPack

#: Licences an imported corpus may carry.
ALLOWED_LICENSES: tuple[str, ...] = (
    "Apache-2.0",
    "MIT",
    "BSD-3-Clause",
    "CC-BY-4.0",
    "CC-BY-SA-4.0",
    "CC0-1.0",
)

#: The tag marking a case imported from a public corpus.
CORPUS_ORIGIN = "origin:corpus"

#: The default target the imported cases exercise.
CORPUS_TARGET = "policyweave-output"


class CorpusError(ValueError):
    """Raised when a corpus entry cannot be imported (licence or shape)."""


class CorpusEntry(BaseModel):
    """One case from a public corpus."""

    id: str
    source: str
    license: str
    title: str
    tags: list[str] = Field(default_factory=list)
    goal: str = ""


def check_license(entry: CorpusEntry) -> None:
    """Fail loudly unless the entry's licence is an allowed OSS/CC licence.

    Raises:
        CorpusError: The licence is not allowed.
    """
    if entry.license not in ALLOWED_LICENSES:
        raise CorpusError(
            f"corpus entry {entry.id!r} has licence {entry.license!r}; "
            f"allowed: {list(ALLOWED_LICENSES)}"
        )


def import_corpus(
    entries: Sequence[CorpusEntry],
    *,
    corpus_name: str,
    version: str = "1.0.0",
    target: str = CORPUS_TARGET,
) -> AttackPack:
    """Map a licence-checked corpus into a runnable attack pack.

    Raises:
        CorpusError: An entry carries a disallowed licence.
    """
    for entry in entries:
        check_license(entry)
    cases = [
        {
            "id": entry.id,
            "title": entry.title,
            "goal": entry.goal or f"Reproduce the imported {entry.source} case",
            "incident_ref": f"corpus:{entry.source}:{entry.id}",
            "target": {"type": target},
            "driver": {"type": "subprocess"},
            "attack": {"steps": [{"tool": "prompt", "args": {}}]},
            "oracle": {"expect": "blocked"},
            "tags": sorted({*entry.tags, CORPUS_ORIGIN, entry.source}),
        }
        for entry in entries
    ]
    return AttackPack.model_validate(
        {
            "pack": {
                "name": corpus_name,
                "version": version,
                "description": f"Imported corpus ({corpus_name})",
                "min_agentdrill": "0.1.0",
                "license": "Apache-2.0",
                "trust": "local",
            },
            "cases": cases,
        }
    )


def require_lint_clean(pack: AttackPack) -> None:
    """Fail loudly unless every case in the pack carries ATLAS + OWASP tags.

    Reuses M17's tagging validator (the single source of truth).

    Raises:
        TaggingError: A case is missing its ATLAS/OWASP tags.
    """
    validate_tagging(pack)
