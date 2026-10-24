"""CI-matrix export (M20 20.4, F72).

``export ci --format github-actions|gitlab`` emits the pack set, manifest and
attestation as a CI matrix; the emitted matrix passes a CI dry-run. Design:
``docs/prd/22-frontier-dx-features.md``.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field

#: The supported CI output formats.
CI_FORMATS: tuple[str, ...] = ("github-actions", "gitlab")


class CiMatrixError(ValueError):
    """Raised when a CI matrix is malformed or a format is unknown."""


class CiMatrix(BaseModel):
    """A CI matrix: the pack set, the run manifest and the attestation labels."""

    packs: list[str] = Field(default_factory=list)
    manifest: dict[str, Any] = Field(default_factory=dict)
    attestation: dict[str, str] = Field(default_factory=dict)


def build_ci_matrix(
    packs: list[str],
    *,
    manifest: dict[str, Any],
    attestation: dict[str, str],
) -> CiMatrix:
    """Build a CI matrix from the pack set, manifest and attestation."""
    return CiMatrix(packs=list(packs), manifest=dict(manifest), attestation=dict(attestation))


def validate_ci_matrix(matrix: CiMatrix) -> None:
    """Fail loudly if the matrix would not pass a CI dry-run.

    Raises:
        CiMatrixError: No packs, no manifest hashes, or no attestation labels.
    """
    if not matrix.packs:
        raise CiMatrixError("CI matrix has no packs")
    if not matrix.manifest.get("hashes"):
        raise CiMatrixError("CI matrix manifest has no hashes")
    if not matrix.attestation:
        raise CiMatrixError("CI matrix has no attestation labels")


def render_ci_matrix(matrix: CiMatrix, *, fmt: str) -> str:
    """Render the matrix for a CI format.

    Raises:
        CiMatrixError: The format is unknown.
    """
    if fmt not in CI_FORMATS:
        raise CiMatrixError(f"unknown CI format: {fmt!r}; known: {list(CI_FORMATS)}")
    payload = matrix.model_dump()
    if fmt == "github-actions":
        return (
            "matrix:\n  include:\n"
            + "\n".join(f"    - pack: {pack}" for pack in matrix.packs)
            + "\n# "
            + json.dumps(payload, sort_keys=True)
            + "\n"
        )
    return "# gitlab matrix\n" + json.dumps(payload, indent=2, sort_keys=True) + "\n"
