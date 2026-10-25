#!/usr/bin/env python3
"""Cross-OS deterministic-metric parity probe (plan FT-E25, PRD 41).

Runs every deterministic scorer in the registry over a fixed battery of
artifacts/scenarios (no LLM, no network, no clock, no randomness) and writes
a canonical outcome file. Run the battery once on the macOS host and once in
the Linux SUT container image; ``compare`` then measures deterministic-metric
outcome parity, which the plan gates at **>= 99.5 %** (FT-E25).

Usage::

    parity_probe.py run --out parity-host.json
    parity_probe.py run --out parity-linux.json        # inside the container
    parity_probe.py compare parity-host.json parity-linux.json \
        --min 0.995 --report parity-report.json

The ``run`` battery is intentionally pure: same fixtures in, same outcomes out,
on any OS/Python. Floats are rounded to 6 decimals so representation-level
noise can never masquerade as a parity miss.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
from typing import Any

# --- battery ---------------------------------------------------------------

TS = {"start": "2026-10-25T00:00:00Z", "end": "2026-10-25T00:01:00Z", "duration_ms": 60000}


def _fixture_battery() -> list[dict[str, Any]]:
    """Build the smoke battery: (fixture, RunArtifact, Scenario, metric_config).

    Each fixture aims at one or more deterministic scorers with both a pass
    and a fail variant, so the parity number is earned on real outcomes —
    not on import-only no-ops.
    """
    from agentdrill.models.artifact import (
        Cost,
        RunArtifact,
        RunOutput,
        RunTimestamps,
        TrajectoryStep,
    )
    from agentdrill.models.pack import Budget, Expected, Scenario, Tool

    def artifact(steps: list[dict[str, Any]], *, final: str | None = None,
                structured: Any = None, cost_usd: float = 0.0, status: str = "completed") -> RunArtifact:
        return RunArtifact(
            id="art-parity",
            scenario_id="sc-parity",
            agent={"name": "parity-probe"},
            timestamp=RunTimestamps(**TS),
            output=RunOutput(final=final, structured=structured),
            trajectory=[TrajectoryStep(**s) for s in steps],
            cost=Cost(input_tokens=10, output_tokens=20, total_tokens=30, cost_usd=cost_usd),
            status=status,  # type: ignore[arg-type]
        )

    def scenario(*, allowed: list[str] | None = None, disallowed: list[str] | None = None,
                 expected: dict[str, Any] | None = None, budget: dict[str, Any] | None = None) -> Scenario:
        return Scenario(
            id="sc-parity",
            title="parity probe",
            input="probe",
            allowed_tools=[Tool(name=n) for n in (allowed or [])],
            disallowed_tools=[Tool(name=n) for n in (disallowed or [])],
            expected=Expected(**expected) if expected else None,  # type: ignore[arg-type]
            budget=Budget(**budget) if budget else None,
        )

    clean_steps = [
        {"type": "tool_call", "tool": "search", "args": {"q": "weather"}},
        {"type": "tool_result", "tool": "search", "result": {"text": "Paris weather: 21C sunny"}},
        {"type": "tool_call", "tool": "finish", "args": {}},
        {"type": "tool_result", "tool": "finish", "result": {"ok": True}},
        {"type": "response", "content": "The weather in Paris is 21C sunny."},
    ]
    messy_steps = [
        {"type": "tool_call", "tool": "rm", "args": {"path": "/"}},
        {"type": "tool_result", "tool": "rm", "result": {"deleted": True}},
        {"type": "tool_call", "tool": "rm", "args": {"path": "/"}},
        {"type": "tool_result", "tool": "rm", "result": {"deleted": True}},
        {"type": "response", "content": "Deleted everything. The moon is made of cheese."},
    ]
    phantom_steps = [
        {"type": "tool_result", "tool": "ghost", "result": {"unmatched": True}},
    ]

    return [
        {
            "fixture": "clean-run",
            "artifact": artifact(clean_steps, final="The weather in Paris is 21C sunny.",
                                 structured={"status": "ok", "count": 3, "items": []}, cost_usd=0.02),
            "scenario": scenario(allowed=["search", "finish"], disallowed=["rm"],
                                 expected={"type": "tool_trace",
                                           "trace": [{"tool": "search", "args": {"q": "weather"}}]},
                                 budget={"max_steps": 10, "max_cost_usd": 0.5}),
        },
        {
            "fixture": "violation-run",
            "artifact": artifact(messy_steps, final="Deleted everything. The moon is made of cheese.",
                                structured={"status": "error"}, cost_usd=0.9),
            "scenario": scenario(allowed=["search"], disallowed=["rm"],
                                 expected={"type": "tool_trace",
                                           "trace": [{"tool": "search", "args": {"q": "weather"}}]},
                                 budget={"max_steps": 2, "max_cost_usd": 0.1}),
        },
        {
            "fixture": "schema-pass",
            "artifact": artifact([], final='{"status": "ok", "count": 3}',
                                 structured={"status": "ok", "count": 3}),
            "scenario": scenario(expected={"type": "schema",
                                           "schema": {"type": "object",
                                                      "required": ["status", "count"],
                                                      "properties": {"status": {"type": "string"},
                                                                     "count": {"type": "number"}}},
                                           "required_fields": ["status", "count"]}),
        },
        {
            "fixture": "schema-fail",
            "artifact": artifact([], final="not json at all", structured=None),
            "scenario": scenario(expected={"type": "schema",
                                           "schema": {"type": "object", "required": ["status"]},
                                           "required_fields": ["status"]}),
        },
        {
            "fixture": "exact-match",
            "artifact": artifact([], final="42"),
            "scenario": scenario(expected={"type": "exact", "value": "42"}),
        },
        {
            "fixture": "exact-miss",
            "artifact": artifact([], final="41"),
            "scenario": scenario(expected={"type": "exact", "value": "42"}),
        },
        {
            "fixture": "grounded-run",
            "artifact": artifact(clean_steps, final="The weather in Paris is 21C sunny."),
            "scenario": scenario(),
        },
        {
            "fixture": "ungrounded-run",
            "artifact": artifact(
                [{"type": "tool_result", "tool": "search", "result": {"text": "Paris weather: 21C sunny"}}],
                final="The moon is made of cheese and taxes were abolished."),
            "scenario": scenario(),
        },
        {
            "fixture": "phantom-run",
            "artifact": artifact(phantom_steps, final="Ghost result appeared."),
            "scenario": scenario(),
        },
        {
            "fixture": "empty-run",
            "artifact": artifact([]),
            "scenario": scenario(budget={"max_steps": 5, "max_cost_usd": 0.01}),
        },
        {
            "fixture": "over-budget-run",
            "artifact": artifact([{"type": "note", "content": f"step {i}"} for i in range(12)],
                                 cost_usd=0.75),
            "scenario": scenario(budget={"max_steps": 4, "max_cost_usd": 0.25}),
        },
    ]


def _deterministic_scorers() -> dict[str, Any]:
    """Every registered scorer from the deterministic package, by name."""
    import agentdrill.scoring  # noqa: F401  (populates the registry)
    from agentdrill.scoring.registry import SCORERS

    return {
        name: cls
        for name, cls in sorted(SCORERS.items())
        if cls.__module__.startswith("agentdrill.scoring.deterministic")
    }


def _outcome_key(scorer: str, fixture: str) -> str:
    return f"{scorer}/{fixture}"


def cmd_run(out_path: str) -> int:
    scorers = _deterministic_scorers()
    if not scorers:
        print("FATAL: no deterministic scorers registered", file=sys.stderr)
        return 2
    outcomes: dict[str, Any] = {}
    for spec in _fixture_battery():
        for name, cls in scorers.items():
            key = _outcome_key(name, spec["fixture"])
            try:
                result = cls().score(spec["artifact"], spec["scenario"], {"threshold": 0.8})
                outcomes[key] = {
                    "passed": result.passed,
                    "score": None if result.score is None else round(float(result.score), 6),
                }
            except Exception as exc:  # the outcome IS the comparison unit
                outcomes[key] = {"passed": None, "score": None, "error": type(exc).__name__}
    doc = {
        "platform": {
            "os": platform.system(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "scorers": sorted(scorers),
        "outcomes": outcomes,
    }
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
        fh.write("\n")
    n = len(outcomes)
    print(f"parity-probe: {n} outcomes ({len(scorers)} scorers x "
          f"{len(_fixture_battery())} fixtures) on {platform.system()}/{platform.machine()} "
          f"py{platform.python_version()} -> {out_path}")
    return 0


def cmd_compare(host_path: str, linux_path: str, minimum: float, report_path: str | None) -> int:
    host = json.load(open(host_path, encoding="utf-8"))
    linux = json.load(open(linux_path, encoding="utf-8"))
    hplat, lplat = host["platform"], linux["platform"]
    if hplat["os"] == lplat["os"]:
        print(f"PARITY-INVALID: both sides are {hplat['os']} — this is not a cross-OS pair",
              file=sys.stderr)
        return 3
    if host["scorers"] != linux["scorers"]:
        print("PARITY-INVALID: scorer sets differ between the two hosts", file=sys.stderr)
        return 3
    hout, lout = host["outcomes"], linux["outcomes"]
    if set(hout) != set(lout):
        missing = sorted(set(hout) ^ set(lout))[:5]
        print(f"PARITY-INVALID: outcome keys differ ({missing}...)", file=sys.stderr)
        return 3
    keys = sorted(hout)
    mismatches = [k for k in keys if hout[k] != lout[k]]
    parity = 1.0 - (len(mismatches) / len(keys)) if keys else 0.0
    report = {
        "hosts": {"host": hplat, "linux": lplat},
        "scorer_count": len(host["scorers"]),
        "outcome_count": len(keys),
        "mismatches": mismatches,
        "parity": round(parity, 6),
        "minimum": minimum,
        "passed": parity >= minimum,
    }
    if report_path:
        with open(report_path, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=1, sort_keys=True)
            fh.write("\n")
    print(f"parity: {parity:.4%} over {len(keys)} deterministic outcomes "
          f"({hplat['os']}/{hplat['machine']} py{hplat['python']} vs "
          f"{lplat['os']}/{lplat['machine']} py{lplat['python']}); "
          f"minimum {minimum:.4%}; {'PASS' if report['passed'] else 'FAIL'}")
    for k in mismatches[:10]:
        print(f"  MISMATCH {k}: host={hout[k]} linux={lout[k]}")
    return 0 if report["passed"] else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    run_p = sub.add_parser("run", help="run the battery, write outcomes")
    run_p.add_argument("--out", required=True)
    cmp_p = sub.add_parser("compare", help="compare two outcome files")
    cmp_p.add_argument("host_file")
    cmp_p.add_argument("linux_file")
    cmp_p.add_argument("--min", type=float, default=0.995)
    cmp_p.add_argument("--report", default=None)
    args = ap.parse_args()
    if args.cmd == "run":
        return cmd_run(args.out)
    return cmd_compare(args.host_file, args.linux_file, args.min, args.report)


if __name__ == "__main__":
    raise SystemExit(main())
