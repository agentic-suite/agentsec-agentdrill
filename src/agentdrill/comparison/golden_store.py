"""Golden/preregistration store (M9 9.6).

Goldens are persisted under ``.agentdrill/goldens/`` and **bound to
``pack@version+hash``**: the file records the pack ref, so a mismatched or
missing golden fails loudly. Design: ``docs/design/comparison.md``.
"""

from __future__ import annotations

from pathlib import Path

from agentdrill.comparison.golden import Golden


class GoldenNotFoundError(KeyError):
    """Raised when no golden exists for a requested ``pack@version+hash``."""


def _unsafe(pack_ref: str) -> bool:
    """Whether ``pack_ref`` could escape the goldens directory."""
    return (
        not pack_ref
        or pack_ref in (".", "..")
        or "/" in pack_ref
        or "\\" in pack_ref
        or pack_ref.startswith("~")
    )


class GoldenStore:
    """Read/write goldens under ``.agentdrill/goldens/``.

    Args:
        base_dir: The goldens directory (default ``.agentdrill/goldens``).
    """

    def __init__(self, base_dir: str | Path = ".agentdrill/goldens") -> None:
        self._base_dir = Path(base_dir)

    @property
    def base_dir(self) -> Path:
        """The goldens directory."""
        return self._base_dir

    def path_for(self, pack_ref: str) -> Path:
        """The golden path for ``pack_ref`` (rejecting an unsafe ref)."""
        if _unsafe(pack_ref):
            raise ValueError(f"unsafe pack ref for a golden: {pack_ref!r}")
        return self._base_dir / f"{pack_ref}.json"

    def exists(self, pack_ref: str) -> bool:
        """Whether a golden exists for ``pack_ref``."""
        return self.path_for(pack_ref).exists()

    def save(self, golden: Golden) -> Path:
        """Write ``golden`` bound to its pack ref; returns the file path."""
        path = self.path_for(golden.pack_ref)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(golden.model_dump_json(indent=2) + "\n", encoding="utf-8")
        return path

    def load(self, pack_ref: str) -> Golden:
        """Load the golden for ``pack_ref`` (loudly if missing or tampered).

        Raises:
            GoldenNotFoundError: No golden file exists for ``pack_ref``.
            ValueError: The stored golden's ``pack_ref`` does not match.
        """
        path = self.path_for(pack_ref)
        if not path.exists():
            raise GoldenNotFoundError(f"no golden for pack ref {pack_ref!r} (looked in {path})")
        golden = Golden.model_validate_json(path.read_text(encoding="utf-8"))
        if golden.pack_ref != pack_ref:
            raise ValueError(
                f"golden pack_ref mismatch: file {path} declares {golden.pack_ref!r}, "
                f"expected {pack_ref!r}"
            )
        return golden
