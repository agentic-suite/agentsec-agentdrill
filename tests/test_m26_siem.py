"""M26 26.6 — SIEM/EDR detection validation (RED → GREEN).

After a drill, query the customer SIEM/EDR for the expected detection within a
time budget and report per case ``detected/alerted/logged/missed`` plus latency
(CUJ-55: of 40 attacks, 31 alerted, 6 logged-only, 3 silent). The SIEM is
injected, so this is offline-testable.
"""

from __future__ import annotations

import pytest

from agentdrill.integrations import (
    DEFAULT_SIEM_BUDGET_MS,
    SiemError,
    SiemEvidence,
    detection_latencies,
    summarize_detection,
    validate_detection,
)

_LEVELS = {
    "c-alerted": SiemEvidence(alerted=True, latency_ms=1200.0),
    "c-detected": SiemEvidence(detected=True, latency_ms=400.0),
    "c-logged": SiemEvidence(logged=True, latency_ms=400_000.0),  # 400 s > 300 s budget
    "c-missed": SiemEvidence(),
}


class _FakeSiem:
    def __init__(self, evidence: dict[str, SiemEvidence]) -> None:
        self._evidence = evidence
        self.seen: list[str] = []

    def query(self, case_id: str, *, since_ms: int, budget_ms: int) -> SiemEvidence:
        self.seen.append(case_id)
        return self._evidence.get(case_id, SiemEvidence())


def test_default_budget_is_five_minutes() -> None:
    assert DEFAULT_SIEM_BUDGET_MS == 300_000


def test_per_case_states_and_latency() -> None:
    siem = _FakeSiem(_LEVELS)
    results = validate_detection(sorted(_LEVELS), siem, since_ms=0)
    states = {r.case_id: r.state for r in results}
    assert states == {
        "c-alerted": "alerted",
        "c-detected": "detected",
        "c-logged": "logged",
        "c-missed": "missed",
    }
    by_case = {r.case_id: r for r in results}
    assert by_case["c-alerted"].latency_ms == 1200.0
    assert by_case["c-alerted"].within_budget is True
    assert by_case["c-logged"].within_budget is False  # 400 s > 300 s budget
    assert by_case["c-missed"].latency_ms is None
    assert siem.seen == sorted(_LEVELS)


def test_summary_and_latency_percentiles() -> None:
    results = validate_detection(sorted(_LEVELS), _FakeSiem(_LEVELS), since_ms=0)
    summary = summarize_detection(results)
    assert summary == {"alerted": 1, "detected": 1, "logged": 1, "missed": 1}
    latencies = detection_latencies(results)
    assert latencies["p50"] > 0
    assert set(latencies) == {"p50", "p95", "max"}


def test_query_failure_fails_loudly() -> None:
    class _Broken:
        def query(self, case_id: str, *, since_ms: int, budget_ms: int) -> SiemEvidence:
            raise RuntimeError("siem down")

    with pytest.raises(SiemError):
        validate_detection(["c1"], _Broken(), since_ms=0)


def test_budget_is_configurable() -> None:
    results = validate_detection(["c-logged"], _FakeSiem(_LEVELS), since_ms=0, budget_ms=30_000)
    assert results[0].within_budget is False
    assert results[0].budget_ms == 30_000


def test_latency_percentiles_fail_loudly_when_none_reported() -> None:
    results = validate_detection(["c-missed"], _FakeSiem(_LEVELS), since_ms=0)
    with pytest.raises(SiemError):
        detection_latencies(results)
