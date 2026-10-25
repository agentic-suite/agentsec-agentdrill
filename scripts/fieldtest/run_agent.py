#!/usr/bin/env python3
"""Run one agent's field matrix (Track B) as a *grounded* assertion.

Deep verification: ``field/run-local.sh`` always exits 0, so a surface check would
pass on a completely failed sweep. This driver:

  1. clones the agent at its pinned SHA (``field/setup.sh --agent``),
  2. runs the local sweep (``field/run-local.sh --tier local --slug``),
  3. reads ``field/results/summary.json`` and **fails** if no scenario passed or
     any scenario failed (a skip already counts as a failure in the runner),
  4. copies the captured agent LLM request/response pairs into ``--llm-out``
     (must-have evidence) and fails if none were captured, and
  5. prints the counts and ``ok: ...``.

Usage::

    python3 run_agent.py SLUG [--tier local] [--llm-out DIR] [--skip-setup]
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FIELD = REPO / "field"
RESULTS = FIELD / "results"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--tier", default="local")
    ap.add_argument("--llm-out", default=None)
    ap.add_argument("--skip-setup", action="store_true")
    args = ap.parse_args(argv)

    if not args.skip_setup:
        setup = subprocess.run(
            ["bash", str(FIELD / "setup.sh"), "--file", str(FIELD / "list.txt"), "--agent", args.slug],
            cwd=REPO, capture_output=True, text=True,
        )
        sys.stdout.write(setup.stdout)
        sys.stderr.write(setup.stderr)
        if setup.returncode != 0:
            print(f"fail: setup failed for {args.slug} (rc={setup.returncode})", file=sys.stderr)
            return 1

    run = subprocess.run(
        ["bash", str(FIELD / "run-local.sh"), "--tier", args.tier, "--slug", args.slug],
        cwd=REPO, capture_output=True, text=True,
    )
    sys.stdout.write(run.stdout)
    sys.stderr.write(run.stderr)

    summary_path = RESULTS / "summary.json"
    if not summary_path.exists():
        print(f"fail: no summary.json at {summary_path}", file=sys.stderr)
        return 1
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"fail: unreadable summary.json: {exc}", file=sys.stderr)
        return 1

    passed = int(summary.get("passed", 0))
    failed = int(summary.get("failed", 0))
    if passed < 1 or failed > 0:
        print(f"fail: matrix {args.slug}: {passed} passed, {failed} failed", file=sys.stderr)
        return 1

    # Copy captured agent LLM request/response pairs (must-have evidence) and the
    # per-scenario verdicts so the committed run carries the full matrix evidence.
    pairs = 0
    if args.llm_out:
        out = Path(args.llm_out)
        out.mkdir(parents=True, exist_ok=True)
        for cap in RESULTS.glob(f"tests/{args.slug}/**/llm/*.json"):
            dest = out / f"{cap.parent.parent.name}-{cap.name}"
            shutil.copyfile(cap, dest)
            pairs += 1
        if pairs == 0:
            print(f"fail: matrix {args.slug}: no LLM request/response pairs captured", file=sys.stderr)
            return 1
        # Per-scenario verdicts (result.json / console.log) for the committed run.
        matrix_out = out.parent / "matrix"
        matrix_out.mkdir(parents=True, exist_ok=True)
        for res in RESULTS.glob(f"tests/{args.slug}/**/result.json"):
            rel = res.relative_to(RESULTS / "tests" / args.slug)
            dest = matrix_out / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(res, dest)

    print(f"ok: matrix {args.slug} ({args.tier}): {passed} passed, 0 failed, {pairs} LLM pair(s)")
    return 0


if __name__ == "__main__":  # pragma: no cover - process entry point
    raise SystemExit(main())
