"""M26 26.4 — CI/code-scanning + ticketing adapters (RED → GREEN).

GitHub code-scanning SARIF upload and a GitLab SAST artifact, plus chat/ticket/
on-call adapters (Slack, Teams, Jira, ServiceNow, PagerDuty, GitHub Issues,
Linear). Delivery is transport-injected and idempotent (stable ticket keys), so a
repeat run does not create duplicate tickets.
"""

from __future__ import annotations

import json

import pytest

from agentdrill.integrations import (
    DELIVERY_DUPLICATE,
    DELIVERY_FAILED,
    DELIVERY_OK,
    TICKET_VENDORS,
    DeliveryResult,
    HttpRequest,
    IntegrationFinding,
    TicketError,
    deliver_tickets,
    github_code_scanning_request,
    render_ticket_body,
    ticket_endpoint,
    ticket_key,
    ticket_request,
    to_gitlab_sast_report,
    to_sarif,
)


def _findings() -> list[IntegrationFinding]:
    return [
        IntegrationFinding(
            case_id="destructive-fs-wipe",
            pack="incidents-core@1.0.0+deadbeef",
            outcome="missed",
            severity="critical",
            tier="T1",
            tags=["ATLAS-AML.T0053", "OWASP-A08"],
            rationale="un-blocked destructive delete",
        ),
        IntegrationFinding(case_id="exfil-secret", outcome="blocked", severity="low"),
    ]


def test_every_vendor_renders_a_body() -> None:
    assert len(TICKET_VENDORS) >= 7
    for vendor in TICKET_VENDORS:
        body = render_ticket_body(vendor, _findings()[0])
        assert isinstance(body, dict) and body


def test_vendor_bodies_carry_the_ticket_and_severity() -> None:
    missed = _findings()[0]
    assert "destructive-fs-wipe" in json.dumps(render_ticket_body("slack", missed))
    jira = render_ticket_body("jira", missed, project="SEC")
    assert jira["fields"]["project"]["key"] == "SEC"
    pagerduty = render_ticket_body("pagerduty", missed)
    assert pagerduty["event_action"] == "trigger"
    assert pagerduty["dedup_key"] == ticket_key(missed)
    assert render_ticket_body("github", missed)["title"]


def test_unknown_vendor_fails_loudly() -> None:
    with pytest.raises(TicketError):
        render_ticket_body("myspace", _findings()[0])  # type: ignore[arg-type]
    with pytest.raises(TicketError):
        ticket_endpoint("myspace", base_url="https://x")  # type: ignore[arg-type]


def test_ticket_key_is_stable_and_dedups() -> None:
    finding = _findings()[0]
    assert ticket_key(finding) == ticket_key(finding)
    assert ticket_key(finding) != ticket_key(_findings()[1])


def test_endpoints_are_vendor_specific() -> None:
    assert ticket_endpoint("jira", base_url="https://jira.example.com").endswith("/rest/api/3/issue")
    assert ticket_endpoint("servicenow", base_url="https://snow.example.com").endswith(
        "/api/now/table/incident"
    )
    assert ticket_endpoint("slack", base_url="https://hooks.slack.com/x") == "https://hooks.slack.com/x"


def test_github_code_scanning_request() -> None:
    request = github_code_scanning_request(
        to_sarif(_findings()),
        owner="acme",
        repo="widgets",
        commit_sha="abc123",
        ref="refs/heads/main",
        token="t0ken",  # noqa: S106 - a fake token in a test
    )
    assert request.method == "POST"
    assert request.url.endswith("/repos/acme/widgets/code-scanning/sarifs")
    assert request.headers["Authorization"] == "Bearer t0ken"
    body = json.loads(request.body)
    assert body["commit_sha"] == "abc123"
    assert json.loads(body["sarif"])["version"] == "2.1.0"


def test_github_code_scanning_requires_a_token() -> None:
    with pytest.raises(TicketError):
        github_code_scanning_request(
            to_sarif(_findings()), owner="acme", repo="widgets", commit_sha="a", ref="r", token=""
        )


def test_gitlab_sast_report_is_valid() -> None:
    report = to_gitlab_sast_report(_findings())
    assert report["version"]
    assert report["scan"]["status"] == "success"
    vulns = {v["name"]: v for v in report["vulnerabilities"]}
    assert set(vulns) == {"destructive-fs-wipe", "exfil-secret"}
    assert vulns["destructive-fs-wipe"]["severity"] == "Critical"
    assert vulns["destructive-fs-wipe"]["identifiers"][0]["value"]


def test_ticket_request_builds_endpoint_headers_and_body() -> None:
    request = ticket_request(
        "jira",
        _findings()[0],
        base_url="https://jira.example.com",
        token="t0ken",  # noqa: S106 - a fake token in a test
        project="SEC",
    )
    assert request.method == "POST"
    assert request.url.endswith("/rest/api/3/issue")
    assert request.headers["Authorization"] == "Bearer t0ken"
    assert json.loads(request.body)["fields"]["project"]["key"] == "SEC"

    github = ticket_request(
        "github", _findings()[0], base_url="https://api.github.com", repo="acme/widgets"
    )
    assert github.url.endswith("/repos/acme/widgets/issues")
    with pytest.raises(TicketError):
        ticket_request("github", _findings()[0], base_url="https://api.github.com")
    with pytest.raises(TicketError):
        ticket_endpoint("github", base_url="https://api.github.com")


def test_deliver_tickets_is_idempotent_and_reports_failures() -> None:
    finding = _findings()[0]
    requests = [
        HttpRequest(
            url=ticket_endpoint("slack", base_url="https://hooks.slack.com/x"),
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps(render_ticket_body("slack", finding)),
        )
    ]
    sent: list[HttpRequest] = []

    def transport(request: HttpRequest) -> bool:
        sent.append(request)
        return True

    first = deliver_tickets(requests, transport=transport)
    assert [r.status for r in first] == [DELIVERY_OK]

    again = requests + requests
    results = deliver_tickets(again, transport=transport)
    assert [r.status for r in results] == [DELIVERY_OK, DELIVERY_DUPLICATE]
    assert len(sent) == 2  # the duplicate was not re-sent

    failing = deliver_tickets(requests, transport=lambda request: False)
    assert [r.status for r in failing] == [DELIVERY_FAILED]
    assert isinstance(failing[0], DeliveryResult)
