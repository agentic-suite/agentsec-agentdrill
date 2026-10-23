"""PR annotations + alerts (M11 11.7, F47).

Annotate a PR with case/stage/evidence/attribution; a regression annotates the
right file. A gate failure posts an alert to a Slack/webhook endpoint. Design:
``docs/design/ci-gate.md``.
"""

from __future__ import annotations

import json
import urllib.request
from collections.abc import Callable, Sequence
from typing import Any

from pydantic import BaseModel

from agentdrill.ci.gating import GateFailure
from agentdrill.comparison.attack_engine import CaseDelta
from agentdrill.comparison.attribution import Attribution

#: A poster delivers a JSON payload to a webhook URL.
Poster = Callable[[str, dict[str, Any]], None]


class Annotation(BaseModel):
    """A PR annotation pointing at the file a finding came from."""

    file: str
    line: int | None = None
    level: str = "warning"
    title: str = ""
    message: str = ""


def annotate(
    change: CaseDelta,
    *,
    file: str,
    line: int | None = None,
    stage: str | None = None,
    evidence: Sequence[str] | None = None,
    attribution: Attribution | None = None,
) -> Annotation:
    """Build an annotation for ``change`` against the file it came from."""
    level = "error" if change.direction == "regressed" else "warning"
    parts = [f"case {change.case_id}: {change.golden_outcome} -> {change.candidate_outcome}"]
    if stage:
        parts.append(f"stage={stage}")
    if evidence:
        parts.append("evidence=" + ",".join(evidence))
    if attribution is not None:
        parts.append(f"attributed_to={attribution.attributed_to}")
    return Annotation(
        file=file,
        line=line,
        level=level,
        title=f"{change.case_id} {change.direction}",
        message="; ".join(parts),
    )


def github_annotation(annotation: Annotation) -> str:
    """Render an :class:`Annotation` as a GitHub Actions workflow command."""
    location = f"file={annotation.file}"
    if annotation.line is not None:
        location += f",line={annotation.line}"
    return f"::{annotation.level} {location}::{annotation.title}: {annotation.message}"


def build_alert(exit_code: int, failures: Sequence[GateFailure]) -> dict[str, Any]:
    """Build the JSON alert payload for a gate failure."""
    return {
        "exit_code": int(exit_code),
        "failures": [failure.model_dump() for failure in failures],
    }


def _post_json(url: str, payload: dict[str, Any]) -> None:
    """POST ``payload`` as JSON to ``url`` (default webhook poster)."""
    request = urllib.request.Request(  # noqa: S310 - operator-configured webhook URL
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(request, timeout=10)  # noqa: S310


def notify(
    webhook: str | None,
    payload: dict[str, Any],
    *,
    poster: Poster | None = None,
) -> None:
    """Post ``payload`` to ``webhook`` (no-op when no webhook is configured)."""
    if not webhook:
        return
    (poster or _post_json)(webhook, payload)
