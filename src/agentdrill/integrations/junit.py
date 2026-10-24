"""JUnit XML emitter (M26 26.1, R74).

Emit findings as JUnit XML so any CI renders them natively: ``missed`` →
``failure``, ``untested`` → ``skipped`` (with a reason); ``degraded`` (a
partial, un-blocked result) is also a ``failure`` so it can never pass CI
unnoticed; only ``blocked`` passes. The document is well-formed XML whose declared counts match
its test cases, checked by :func:`validate_junit` before it is returned.
Design: ``docs/design/integrations.md``; PRD 38 R74.
"""

from __future__ import annotations

from collections.abc import Sequence
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape, quoteattr

from agentdrill.integrations.model import IntegrationFinding

#: The default suite name.
DEFAULT_SUITE_NAME = "agentdrill"


class JUnitError(ValueError):
    """Raised when a JUnit document is malformed or its counts do not match."""


def _testcase(finding: IntegrationFinding) -> str:
    """One ``<testcase>`` element as text, with its failure/skip child."""
    classname = finding.pack or DEFAULT_SUITE_NAME
    open_tag = (
        f"<testcase classname={quoteattr(classname)} "
        f"name={quoteattr(finding.case_id)} time=\"0\">"
    )
    if finding.outcome == "missed":
        body = f"<failure message=\"missed\">{escape(finding.rationale or 'missed')}</failure>"
    elif finding.outcome == "degraded":
        body = f"<failure message=\"degraded\">{escape(finding.rationale or 'degraded')}</failure>"
    elif finding.outcome == "untested":
        body = "<skipped message=\"untested\"/>"
    else:
        body = ""
    return f"{open_tag}{body}</testcase>"


def _counts(findings: Sequence[IntegrationFinding]) -> tuple[int, int, int]:
    """``(tests, failures, skipped)`` for a set of findings."""
    failures = sum(1 for f in findings if f.outcome in ("missed", "degraded"))
    skipped = sum(1 for f in findings if f.outcome == "untested")
    return len(findings), failures, skipped


def to_junit(
    findings: Sequence[IntegrationFinding], *, suite_name: str = DEFAULT_SUITE_NAME
) -> str:
    """Build a JUnit XML document from ``findings``.

    Raises:
        JUnitError: The built document fails :func:`validate_junit`.
    """
    tests, failures, skipped = _counts(findings)
    cases = "\n".join(f"    {_testcase(f)}" for f in findings)
    suite_attrs = f'tests="{tests}" failures="{failures}" skipped="{skipped}"'
    document = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f"<testsuites {suite_attrs}>\n"
        f"  <testsuite name={quoteattr(suite_name)} {suite_attrs}>\n"
        f"{cases}\n"
        "  </testsuite>\n"
        "</testsuites>\n"
    )
    validate_junit(document)
    return document


def validate_junit(document: str) -> None:
    """Validate a JUnit document: well-formed, correctly rooted, counts match.

    Raises:
        JUnitError: The document is not parseable, is not a JUnit document, or
            a declared count disagrees with the actual test cases.
    """
    # Reject any DTD/entity declaration: the emitted document never carries one,
    # and banning it removes the entity-expansion ("billion laughs") vector that
    # makes stdlib XML parsing of a third-party document unsafe (S314).
    if "<!DOCTYPE" in document or "<!ENTITY" in document:
        raise JUnitError("JUnit document must not declare a DTD or entities")
    try:
        root = ET.fromstring(document)  # noqa: S314 - DTD/entities rejected above
    except ET.ParseError as exc:
        raise JUnitError(f"malformed XML: {exc}") from exc

    if root.tag not in ("testsuites", "testsuite"):
        raise JUnitError(f"not a JUnit document: root <{root.tag}>")
    suites = root.findall("testsuite") if root.tag == "testsuites" else [root]
    if not suites:
        raise JUnitError("JUnit document has no <testsuite>")
    for suite in suites:
        cases = suite.findall("testcase")
        failures = sum(1 for c in cases if c.find("failure") is not None)
        skipped = sum(1 for c in cases if c.find("skipped") is not None)
        expected = {
            "tests": len(cases),
            "failures": failures,
            "skipped": skipped,
        }
        for attr, actual in expected.items():
            declared = suite.get(attr)
            if declared is None:
                raise JUnitError(f"<testsuite> missing {attr!r} attribute")
            if declared != str(actual):
                raise JUnitError(
                    f"<testsuite> {attr}={declared} does not match actual {actual}"
                )
        for case in cases:
            if not case.get("name"):
                raise JUnitError("<testcase> missing name attribute")
