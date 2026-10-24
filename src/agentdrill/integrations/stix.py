"""STIX 2.1 emitter (M26 26.3, R74).

Emit a STIX 2.1 bundle: an ``identity`` for the tool, an optional
``threat-actor`` from an :class:`~agentdrill.interop.profiles.AdversaryProfile`
card, one ``vulnerability`` per case (with ATLAS/OWASP external references) and
the ``relationship`` linking the tool to each. :func:`validate_stix` checks the
required STIX 2.1 object fields and the ``<type>--<uuid>`` id form.
Ids are derived (``uuid5``) so bundles are stable and dedup-able.
Design: ``docs/design/integrations.md``; PRD 38 R74.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

from agentdrill.integrations.model import IntegrationFinding
from agentdrill.interop.profiles import AdversaryProfile

#: The STIX version this emitter targets.
STIX_VERSION = "2.1"

#: A deterministic default ``created``/``modified`` timestamp (RFC3339, ms).
STIX_EPOCH = "1970-01-01T00:00:00.000Z"


class STIXValidationError(ValueError):
    """Raised when a STIX object is missing a required field or has a bad id."""


def _sid(type_: str, key: str) -> str:
    """A stable STIX id ``<type>--<uuid>`` for ``type_``/``key``."""
    return f"{type_}--{uuid5(NAMESPACE_URL, f'agentdrill:{type_}:{key}')}"


def _external_references(tags: Sequence[str]) -> list[dict[str, str]]:
    """ATLAS/OWASP tags as STIX ``external_references``."""
    references: list[dict[str, str]] = []
    for tag in tags:
        if tag.startswith("ATLAS-"):
            references.append({"source_name": "mitre-atlas", "external_id": tag[len("ATLAS-") :]})
        elif tag.startswith("OWASP-"):
            references.append({"source_name": "owasp", "external_id": tag[len("OWASP-") :]})
    return references


def to_stix_bundle(
    findings: Sequence[IntegrationFinding],
    *,
    profile: AdversaryProfile | None = None,
    created: str = STIX_EPOCH,
) -> dict[str, Any]:
    """Emit a STIX 2.1 bundle of a drill's findings.

    Raises:
        STIXValidationError: The built bundle fails :func:`validate_stix`.
        ValueError: ``profile`` is present but incomplete.
    """
    identity_id = _sid("identity", "agentdrill")
    objects: list[dict[str, Any]] = [
        {
            "type": "identity",
            "spec_version": STIX_VERSION,
            "id": identity_id,
            "created": created,
            "modified": created,
            "name": "agentdrill",
            "identity_class": "system",
        }
    ]
    if profile is not None:
        profile.validate_profile()
        objects.append(
            {
                "type": "threat-actor",
                "spec_version": STIX_VERSION,
                "id": _sid("threat-actor", profile.who),
                "created": created,
                "modified": created,
                "name": profile.who,
                "description": (
                    f"{profile.what}; objective: {profile.objective}; source: {profile.source}"
                ),
            }
        )
    for finding in findings:
        vulnerability_id = _sid("vulnerability", finding.case_id)
        vulnerability: dict[str, Any] = {
            "type": "vulnerability",
            "spec_version": STIX_VERSION,
            "id": vulnerability_id,
            "created": created,
            "modified": created,
            "name": finding.case_id,
            "description": finding.rationale or f"{finding.outcome}: {finding.case_id}",
        }
        references = _external_references(finding.tags)
        if references:
            vulnerability["external_references"] = references
        objects.append(vulnerability)
        objects.append(
            {
                "type": "relationship",
                "spec_version": STIX_VERSION,
                "id": _sid("relationship", finding.case_id),
                "created": created,
                "modified": created,
                "relationship_type": "related-to",
                "source_ref": identity_id,
                "target_ref": vulnerability_id,
            }
        )
    bundle: dict[str, Any] = {
        "type": "bundle",
        "spec_version": STIX_VERSION,
        "id": _sid("bundle", "drill"),
        "objects": objects,
    }
    validate_stix(bundle)
    return bundle


def validate_stix(bundle: dict[str, Any]) -> None:
    """Validate the required STIX 2.1 fields and id form.

    Raises:
        STIXValidationError: The bundle or an object is malformed.
    """
    if bundle.get("type") != "bundle":
        raise STIXValidationError(f"not a STIX bundle: type={bundle.get('type')!r}")
    if bundle.get("spec_version") != STIX_VERSION:
        raise STIXValidationError(f"unexpected spec_version {bundle.get('spec_version')!r}")
    _check_id("bundle", bundle.get("id"))
    objects = bundle.get("objects")
    if not isinstance(objects, list):
        raise STIXValidationError("bundle.objects must be a list")
    for obj in objects:
        for field in ("type", "id", "spec_version", "created", "modified"):
            if field not in obj:
                raise STIXValidationError(f"STIX object missing required field {field!r}")
        if obj["spec_version"] != STIX_VERSION:
            raise STIXValidationError(f"unexpected spec_version {obj['spec_version']!r}")
        _check_id(obj["type"], obj["id"])
        if obj["type"] in ("identity", "threat-actor", "vulnerability") and not obj.get("name"):
            raise STIXValidationError(f"STIX {obj['type']} missing name")
        if obj["type"] == "relationship" and not obj.get("relationship_type"):
            raise STIXValidationError("STIX relationship missing relationship_type")


def _check_id(type_: str, id_: object) -> None:
    """Fail loudly unless ``id_`` is ``<type>--<uuid>``."""
    prefix = f"{type_}--"
    if not isinstance(id_, str) or not id_.startswith(prefix):
        raise STIXValidationError(f"id {id_!r} must start with {prefix!r}")
    try:
        UUID(id_[len(prefix) :])
    except ValueError as exc:
        raise STIXValidationError(f"id {id_!r} does not carry a valid UUID") from exc
