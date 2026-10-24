"""CI / code-scanning emitters (M26 26.4, R74).

Upload a SARIF log to **GitHub code scanning** (``POST
/repos/{owner}/{repo}/code-scanning/sarifs``) and emit a **GitLab SAST** report
artifact — so findings annotate a PR (CUJ-54) and appear in the Security tab.
Credentials are passed per call and never stored. Design:
``docs/design/integrations.md``; PRD 38 R74.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from agentdrill.integrations.model import IntegrationFinding
from agentdrill.integrations.ticketing import TicketError
from agentdrill.integrations.transport import HttpRequest

#: The GitHub REST base URL.
GITHUB_API_BASE = "https://api.github.com"

#: The GitLab SAST report schema version emitted here.
GITLAB_SAST_VERSION = "15.0.0"

#: The GitLab SAST severity per rated severity.
_GITLAB_SEVERITY: dict[str, str] = {
    "critical": "Critical",
    "high": "High",
    "medium": "Medium",
    "low": "Low",
}

#: Fallback GitLab severity per outcome.
_GITLAB_OUTCOME_SEVERITY: dict[str, str] = {
    "missed": "High",
    "degraded": "Medium",
    "blocked": "Info",
    "untested": "Info",
}


class CodeScanningError(TicketError):
    """Raised when a code-scanning upload cannot be built."""


def github_code_scanning_request(
    sarif_log: dict[str, Any],
    *,
    owner: str,
    repo: str,
    commit_sha: str,
    ref: str,
    token: str,
    base_url: str = GITHUB_API_BASE,
) -> HttpRequest:
    """Build the GitHub code-scanning SARIF upload request.

    Raises:
        CodeScanningError: No token is supplied (the upload is authenticated).
    """
    if not token:
        raise CodeScanningError("GitHub code-scanning upload requires a token")
    body = json.dumps(
        {"commit_sha": commit_sha, "ref": ref, "sarif": json.dumps(sarif_log)}
    )
    return HttpRequest(
        url=f"{base_url.rstrip('/')}/repos/{owner}/{repo}/code-scanning/sarifs",
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
        body=body,
        key=f"github-code-scanning:{owner}/{repo}@{commit_sha}",
    )


def _severity(finding: IntegrationFinding) -> str:
    return _GITLAB_SEVERITY.get(
        finding.severity or "", _GITLAB_OUTCOME_SEVERITY[finding.outcome]
    )


def to_gitlab_sast_report(
    findings: Sequence[IntegrationFinding],
    *,
    scanner_id: str = "agentdrill",
    scanner_name: str = "agentdrill",
    scanner_version: str = "0.1.0",
    start_time: str = "1970-01-01T00:00:00Z",
    end_time: str = "1970-01-01T00:00:00Z",
) -> dict[str, Any]:
    """Emit a GitLab SAST report (``gl-sast-report.json``) for the findings."""
    scanner = {
        "id": scanner_id,
        "name": scanner_name,
        "version": scanner_version,
        "vendor": {"name": "agentdrill"},
    }
    vulnerabilities: list[dict[str, Any]] = []
    for finding in findings:
        vulnerabilities.append(
            {
                "id": str(uuid5(NAMESPACE_URL, f"agentdrill:sast:{finding.case_id}")),
                "category": "sast",
                "name": finding.case_id,
                "message": finding.rationale or f"{finding.outcome}: {finding.case_id}",
                "description": finding.rationale or f"{finding.outcome}: {finding.case_id}",
                "severity": _severity(finding),
                "confidence": "High",
                "scanner": {"id": scanner_id, "name": scanner_name},
                "location": {"file": finding.pack or "agentdrill", "start_line": 1},
                "identifiers": [
                    {
                        "type": "agentdrill_rule",
                        "name": finding.case_id,
                        "value": finding.partial_fingerprint(),
                    }
                ],
            }
        )
    return {
        "version": GITLAB_SAST_VERSION,
        "scan": {
            "analyzer": scanner,
            "scanner": scanner,
            "type": "sast",
            "status": "success",
            "start_time": start_time,
            "end_time": end_time,
        },
        "vulnerabilities": vulnerabilities,
    }
