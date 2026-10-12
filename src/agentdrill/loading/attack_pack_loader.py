"""Load and strictly validate attack packs (M2 work item 2.2).

Validation is two-stage, mirroring the shipped scenario loader: a lightweight
structural pass that raises :class:`~agentdrill.models.errors.PackParseError`
with file/line context and actionable messages, then a pydantic pass that
coerces the raw data into :class:`~agentdrill.models.attack_pack.AttackPack`.

The **path-safety invariant** ``^[a-zA-Z0-9_-]+$`` is enforced on every case id
*before any path use* — this closes the predecessor's traversal gap at the
foundation (WBS 2.2, predecessor gap G3).

Reference: ``docs/design/pack-format.md`` · ``docs/reference/pack-format-spec.md``.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from agentdrill.loading.attack_registry import resolve_case
from agentdrill.models.attack_pack import AttackPack
from agentdrill.models.errors import PackParseError

#: Case ids must be path-safe: enforced before any path use.
CASE_ID_PATTERN = r"^[a-zA-Z0-9_-]+$"

#: Required fields in the ``pack`` block.
REQUIRED_PACK_FIELDS = ("name", "version", "description", "min_agentdrill", "license", "trust")

#: Required fields in every case.
REQUIRED_CASE_FIELDS = (
    "id",
    "title",
    "goal",
    "incident_ref",
    "target",
    "driver",
    "attack",
    "oracle",
)

#: Permitted ``pack.trust`` values.
TRUST_LEVELS = ("built-in", "local", "external")


def load_attack_pack(path: str | Path) -> AttackPack:
    """Parse and strictly validate an attack pack from a YAML or JSON file.

    Args:
        path: Path to the pack file (``.yaml``, ``.yml``, or ``.json``).

    Returns:
        A validated :class:`AttackPack`.

    Raises:
        PackParseError: If the file is missing, malformed, or fails structural
            or schema validation (carries ``file``/``line`` where known).
    """
    p = Path(path)
    if not p.exists():
        raise PackParseError(f"pack file not found: {p}", file=str(p))
    try:
        raw = p.read_text(encoding="utf-8")
    except OSError as exc:
        raise PackParseError(f"could not read pack: {exc}", file=str(p)) from exc

    data = _parse(raw, p)
    _validate_structure(data, p)
    try:
        pack = AttackPack.model_validate(data)
    except ValidationError as exc:
        raise PackParseError(f"invalid pack structure: {exc}", file=str(p)) from exc
    for case in pack.cases:
        resolve_case(case, pack.pack.trust)
    _validate_links(pack, p)
    _check_min_agentdrill(pack, p)
    pack.pack.hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return pack


def _version_tuple(value: str) -> tuple[int, ...]:
    """Parse the leading numeric components of a version string."""
    parts = [int(p) for p in re.findall(r"\d+", value)[:3]]
    return tuple(parts) if parts else (0,)


def _check_min_agentdrill(pack: AttackPack, path: Path) -> None:
    """Fail loudly when the pack requires a newer agentdrill than this one."""
    from agentdrill import __version__

    if _version_tuple(pack.pack.min_agentdrill) > _version_tuple(__version__):
        raise PackParseError(
            f"pack requires min_agentdrill {pack.pack.min_agentdrill} but this "
            f"is agentdrill {__version__}",
            file=str(path),
        )


def _validate_links(pack: AttackPack, path: Path) -> None:
    """Fail loudly if a case's ``benign_twin`` reference does not resolve."""
    ids = {case.id for case in pack.cases}
    for case in pack.cases:
        if case.benign_twin is not None and case.benign_twin not in ids:
            raise PackParseError(
                f"case {case.id}: benign_twin {case.benign_twin!r} does not "
                "reference a case in this pack",
                file=str(path),
            )


def is_attack_pack(path: str | Path) -> bool:
    """Return True if ``path`` looks like an attack pack (has a ``cases`` list)."""
    p = Path(path)
    try:
        data = _parse(p.read_text(encoding="utf-8"), p)
    except (OSError, PackParseError):
        return False
    return isinstance(data, dict) and isinstance(data.get("cases"), list)


def discover_attack_packs(search_paths: list[str] | None = None) -> list[AttackPack]:
    """Discover and load every attack pack under ``search_paths``.

    Defaults to ``["packs"]``. Non-pack files are skipped; an attack pack that
    fails validation raises (loudly) rather than being silently dropped.

    Args:
        search_paths: Directories to search. Defaults to ``["packs"]``.

    Returns:
        Loaded :class:`AttackPack` instances, ordered by pack name.
    """
    if search_paths is None:
        search_paths = ["packs"]
    found: list[AttackPack] = []
    for search_path in search_paths:
        root = Path(search_path)
        if not root.is_dir():
            continue
        for pattern in ("*.yaml", "*.yml", "*.json"):
            for file_path in sorted(root.rglob(pattern)):
                if is_attack_pack(file_path):
                    found.append(load_attack_pack(file_path))
    return sorted(found, key=lambda pack: pack.pack.name)


def _parse(raw: str, path: Path) -> object:
    """Parse YAML (primary) or JSON (secondary) with line-number reporting."""
    if path.suffix.lower() == ".json":
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise PackParseError(
                f"malformed JSON: {exc.msg}", file=str(path), line=exc.lineno
            ) from exc
    try:
        return yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        line = mark.line + 1 if mark is not None else None
        raise PackParseError(f"malformed YAML: {exc}", file=str(path), line=line) from exc


def _validate_structure(data: object, path: Path) -> None:
    """Run structural checks that give better errors than pydantic's.

    Checks the ``pack`` block, a non-empty ``cases`` list, per-case required
    fields, duplicate ids, the path-safety invariant, coherent budgets, and
    the trust/expectation enumerations.

    Raises:
        PackParseError: If any check fails.
    """
    if not isinstance(data, dict):
        raise PackParseError("pack must be a mapping with `pack` and `cases`", file=str(path))

    pack = data.get("pack")
    if not isinstance(pack, dict):
        raise PackParseError("missing required `pack` metadata block", file=str(path))
    for field in REQUIRED_PACK_FIELDS:
        if field not in pack:
            raise PackParseError(f"pack metadata missing required field: {field}", file=str(path))
    trust = pack["trust"]
    if trust not in TRUST_LEVELS:
        raise PackParseError(
            f"pack.trust must be one of {TRUST_LEVELS}: got {trust!r}", file=str(path)
        )

    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        raise PackParseError("missing or empty required `cases` list", file=str(path))

    seen: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise PackParseError(f"case {index} must be a mapping", file=str(path))
        for field in REQUIRED_CASE_FIELDS:
            if field not in case:
                raise PackParseError(
                    f"case {index} missing required field: {field}", file=str(path)
                )
        _check_case_id(case["id"], index, seen, path)
        _check_budget(case, path)


def _check_case_id(case_id: object, index: int, seen: set[str], path: Path) -> None:
    """Enforce id presence, uniqueness, and the path-safety invariant."""
    if not isinstance(case_id, str) or not re.match(CASE_ID_PATTERN, case_id):
        raise PackParseError(
            f"case {index}: id {case_id!r} is not path-safe (must match {CASE_ID_PATTERN})",
            file=str(path),
        )
    if case_id in seen:
        raise PackParseError(f"duplicate case id: {case_id}", file=str(path))
    seen.add(case_id)


def _check_budget(case: dict[str, Any], path: Path) -> None:
    """Reject incoherent (negative or non-numeric) per-case budgets."""
    budget = case.get("budget")
    if budget is None:
        return
    if not isinstance(budget, dict):
        raise PackParseError(f"case {case['id']} budget must be a mapping", file=str(path))
    for field in ("max_steps", "max_tokens", "max_cost_usd"):
        value = budget.get(field)
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, int | float) or value < 0:
            raise PackParseError(
                f"case {case['id']} budget {field} must be a non-negative number: {value!r}",
                file=str(path),
            )
