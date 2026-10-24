"""Normalized integration findings (M26 26.1).

An :class:`IntegrationFinding` is the **neutral projection** of one case result
that every outbound emitter (SARIF, JUnit — and later OCSF/OSCAL/STIX) renders.
It is deliberately small and format-agnostic: identity (``case_id``), the honest
outcome, the standards tags (ATLAS/OWASP), and the evidence fields the PRD
requires on every published number (attacker ``tier``/``k``, independent
``witness_ref``).

Projection, not a second source of truth: :func:`findings_from_report` derives
findings from the M10 :class:`~agentdrill.reporting.model.Report`. Enrichment
that the report does not carry (tier, witness ref, waivers) is applied by the
owning milestone's module at the call site — M24 for tier/k, M23 for witness
refs, M28 for waivers. Design: ``docs/design/integrations.md``.
"""

from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, Field

from agentdrill.reporting.model import Report

#: A case's outcome, in the honest vocabulary shared by the reporter.
FindingOutcome = Literal["blocked", "missed", "degraded", "untested"]

#: The outcomes a :class:`~agentdrill.reporting.model.Report` row may carry.
_REPORT_OUTCOMES: frozenset[str] = frozenset({"blocked", "missed", "degraded", "untested"})

#: SARIF result level per outcome (SARIF 2.1.0: none/note/warning/error).
SARIF_LEVEL: dict[str, str] = {
    "missed": "error",
    "degraded": "warning",
    "blocked": "none",
    "untested": "note",
}


class IntegrationFinding(BaseModel):
    """A format-agnostic projection of one case result for emission.

    Attributes:
        case_id: The case identity (the SARIF rule id).
        outcome: blocked / missed / degraded / untested.
        pack: ``name@version+hash`` the case belongs to (evidence binding).
        tags: MITRE ATLAS / OWASP tags carried by the case.
        severity: The rated severity (M10 rubric), when rated.
        tier: The attacker tier the result was measured at (M24), when known.
        k: The ``k`` in ``Hold@k``/``ASR@k`` (M24), when known.
        witness_ref: The independent effect-witness reference (M23), when known.
        rationale: Human rationale / message.
        trace_ref: Reference to the stored trace (M10 ``TraceStore``).
        waived: True when an active waiver suppresses the finding (M28).
        waiver_reason: The waiver's justification (required when waived).
    """

    case_id: str
    outcome: FindingOutcome
    pack: str | None = None
    tags: list[str] = Field(default_factory=list)
    severity: str | None = None
    tier: str | None = None
    k: int | None = None
    witness_ref: str | None = None
    rationale: str = ""
    trace_ref: str | None = None
    waived: bool = False
    waiver_reason: str | None = None

    @property
    def rule_id(self) -> str:
        """The SARIF rule id — the case id."""
        return self.case_id

    def partial_fingerprint(self) -> str:
        """A stable fingerprint that survives across runs.

        Identity is ``pack_ref + case_id`` only: timestamps, costs and trace
        refs must not change a result's identity, or dedup (≥ 99 %) breaks.
        """
        digest = hashlib.sha256()
        digest.update((self.pack or "").encode("utf-8"))
        digest.update(b"\x00")
        digest.update(self.case_id.encode("utf-8"))
        return digest.hexdigest()


def findings_from_report(report: Report) -> list[IntegrationFinding]:
    """Project a M10 :class:`~agentdrill.reporting.model.Report` into findings.

    Raises:
        ValueError: A row carries an outcome outside the honest vocabulary
            (``blocked``/``missed``/``degraded``/``untested``) — a silent
            coercion would misreport a result.
    """
    findings: list[IntegrationFinding] = []
    for row in report.rows:
        if row.outcome not in _REPORT_OUTCOMES:
            raise ValueError(
                f"case {row.case_id!r}: unknown outcome {row.outcome!r}; "
                f"expected one of {sorted(_REPORT_OUTCOMES)}"
            )
        findings.append(
            IntegrationFinding(
                case_id=row.case_id,
                outcome=row.outcome,  # type: ignore[arg-type]
                pack=row.pack or report.pack_ref,
                tags=list(row.tags),
                severity=row.severity,
                rationale=row.rationale,
                trace_ref=row.trace_ref,
            )
        )
    return findings
