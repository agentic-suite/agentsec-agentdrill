"""Chat / ticket / on-call adapters (M26 26.4, R74).

Render a finding into the payload a buyer's tool expects — Slack, Teams, Jira,
ServiceNow, PagerDuty, GitHub Issues, Linear — and build the delivery request.
Tickets carry a **stable key** (``pack:case``) so a re-run is idempotent and the
duplicate-ticket rate stays ≤ 2 %. Status sync against the exposure ledger is the
M28 seam. Design: ``docs/design/integrations.md``; PRD 38 R74.
"""

from __future__ import annotations

import json
from typing import Any, Literal

from agentdrill.integrations.model import IntegrationFinding
from agentdrill.integrations.transport import HttpRequest

#: The supported ticket/chat/on-call vendors.
TicketVendor = Literal["slack", "teams", "jira", "servicenow", "pagerduty", "github", "linear"]

#: All supported vendors, in a stable order.
TICKET_VENDORS: tuple[TicketVendor, ...] = (
    "slack",
    "teams",
    "jira",
    "servicenow",
    "pagerduty",
    "github",
    "linear",
)

#: Default endpoints for vendors with a public SaaS API.
_DEFAULT_ENDPOINT: dict[str, str] = {
    "pagerduty": "https://events.pagerduty.com/v2/enqueue",
    "linear": "https://api.linear.app/graphql",
}

#: Vendor severity labels per rated severity.
_SEVERITY: dict[str, str] = {
    "critical": "critical",
    "high": "high",
    "medium": "medium",
    "low": "low",
}


class TicketError(ValueError):
    """Raised when a vendor is unknown or a request cannot be built."""


def ticket_key(finding: IntegrationFinding) -> str:
    """The stable dedup key for a finding's ticket (``pack:case``)."""
    return f"{finding.pack or 'agentdrill'}:{finding.case_id}"


def _summary(finding: IntegrationFinding) -> str:
    return f"[agentdrill] {finding.case_id}: {finding.outcome}"


def _severity(finding: IntegrationFinding) -> str:
    return _SEVERITY.get(finding.severity or "", "unknown")


def _body_slack(finding: IntegrationFinding, **_: Any) -> dict[str, Any]:
    return {
        "text": _summary(finding),
        "attachments": [
            {
                "color": "#cc0000" if finding.outcome == "missed" else "#e0a800",
                "title": finding.case_id,
                "text": finding.rationale or _summary(finding),
                "fields": [
                    {"title": "outcome", "value": finding.outcome, "short": True},
                    {"title": "severity", "value": _severity(finding), "short": True},
                    {"title": "tier", "value": finding.tier or "-", "short": True},
                    {"title": "witness", "value": finding.witness_ref or "-", "short": True},
                ],
            }
        ],
    }


def _body_teams(finding: IntegrationFinding, **_: Any) -> dict[str, Any]:
    return {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "summary": _summary(finding),
        "title": finding.case_id,
        "text": finding.rationale or _summary(finding),
        "themeColor": "cc0000" if finding.outcome == "missed" else "e0a800",
    }


def _body_jira(
    finding: IntegrationFinding, *, project: str | None = None, **_: Any
) -> dict[str, Any]:
    return {
        "fields": {
            "project": {"key": project or "SEC"},
            "summary": f"[agentdrill] {finding.case_id}",
            "description": finding.rationale or _summary(finding),
            "issuetype": {"name": "Bug"},
            "labels": ["agentdrill", finding.outcome],
        }
    }


def _body_servicenow(finding: IntegrationFinding, **_: Any) -> dict[str, Any]:
    return {
        "short_description": f"[agentdrill] {finding.case_id}",
        "description": finding.rationale or _summary(finding),
        "category": "security",
        "impact": "1" if finding.severity == "critical" else "2",
        "urgency": "1" if finding.outcome == "missed" else "2",
    }


def _body_pagerduty(finding: IntegrationFinding, **_: Any) -> dict[str, Any]:
    return {
        "event_action": "trigger",
        "dedup_key": ticket_key(finding),
        "payload": {
            "summary": _summary(finding),
            "source": "agentdrill",
            "severity": _severity(finding),
            "custom_details": {
                "outcome": finding.outcome,
                "tier": finding.tier,
                "witness": finding.witness_ref,
                "pack": finding.pack,
            },
        },
    }


def _body_github(finding: IntegrationFinding, **_: Any) -> dict[str, Any]:
    body = finding.rationale or _summary(finding)
    return {
        "title": f"[agentdrill] {finding.case_id}",
        "body": f"{body}\n\n- outcome: `{finding.outcome}`\n- severity: `{_severity(finding)}`",
        "labels": ["agentdrill", "security"],
    }


def _body_linear(
    finding: IntegrationFinding, *, team_id: str | None = None, **_: Any
) -> dict[str, Any]:
    return {
        "title": f"[agentdrill] {finding.case_id}",
        "description": finding.rationale or _summary(finding),
        "priority": 1 if finding.outcome == "missed" else 3,
        "teamId": team_id,
    }


_BODY_RENDERERS: dict[str, Any] = {
    "slack": _body_slack,
    "teams": _body_teams,
    "jira": _body_jira,
    "servicenow": _body_servicenow,
    "pagerduty": _body_pagerduty,
    "github": _body_github,
    "linear": _body_linear,
}


def render_ticket_body(
    vendor: str,
    finding: IntegrationFinding,
    *,
    project: str | None = None,
    team_id: str | None = None,
) -> dict[str, Any]:
    """Render ``finding`` into ``vendor``'s payload shape.

    Raises:
        TicketError: The vendor is unknown.
    """
    renderer = _BODY_RENDERERS.get(vendor)
    if renderer is None:
        raise TicketError(f"unknown ticket vendor: {vendor!r}; known: {list(TICKET_VENDORS)}")
    body: dict[str, Any] = renderer(finding, project=project, team_id=team_id)
    return body


def ticket_endpoint(
    vendor: str, *, base_url: str, repo: str | None = None
) -> str:
    """The endpoint for ``vendor``, derived from ``base_url``.

    Raises:
        TicketError: The vendor is unknown.
    """
    if vendor not in _BODY_RENDERERS:
        raise TicketError(f"unknown ticket vendor: {vendor!r}; known: {list(TICKET_VENDORS)}")
    if vendor == "jira":
        return f"{base_url.rstrip('/')}/rest/api/3/issue"
    if vendor == "servicenow":
        return f"{base_url.rstrip('/')}/api/now/table/incident"
    if vendor == "github":
        if not repo:
            raise TicketError("github ticket endpoint requires repo='owner/name'")
        return f"{base_url.rstrip('/')}/repos/{repo}/issues"
    if vendor in ("slack", "teams"):
        return base_url
    return base_url or _DEFAULT_ENDPOINT[vendor]


def ticket_request(
    vendor: str,
    finding: IntegrationFinding,
    *,
    base_url: str,
    token: str | None = None,
    project: str | None = None,
    team_id: str | None = None,
    repo: str | None = None,
) -> HttpRequest:
    """Build the delivery request for one ticket.

    Raises:
        TicketError: The vendor is unknown or its endpoint is under-specified.
    """
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return HttpRequest(
        url=ticket_endpoint(vendor, base_url=base_url, repo=repo),
        method="POST",
        headers=headers,
        body=json.dumps(render_ticket_body(vendor, finding, project=project, team_id=team_id)),
        key=ticket_key(finding),
    )
