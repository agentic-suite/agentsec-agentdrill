#!/usr/bin/env python3
"""Fill docs/field-test/<FT_VERSION>/FIELD_TEST_REPORT.md from the run results.

Reads every field-test/<FT_VERSION>/results/<suite>/cases/<ID>/verdict.json and
rewrites these report sections:

  * Scenario Results (Master Table)      -- every case: PASS | FAIL | not run
  * Per-Suite Results                    -- per-suite rollup
  * Root Cause Analysis                  -- one block per FAIL (evidence)
  * Defect Catalogue                     -- one row per FAIL

Status vocabulary is exactly **PASS | FAIL | not run | N/A** (per the run
request). `declared` (an unavailable P/F|D environment) is reported as `not run`
with a note, since it is neither a pass nor a fail.

Usage: python3 scripts/fieldtest/build_report.py
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FT_VERSION = os.environ.get("FT_VERSION", "v0.1.0")
RESULTS = REPO / "field-test" / FT_VERSION / "results"
REGISTRY = REPO / "scripts/fieldtest/cases/registry.json"
REPORT = REPO / f"docs/field-test/{FT_VERSION}/FIELD_TEST_REPORT.md"

SUITES = ["track-a", "demos", "track-b", "track-c", "ft-e-p0", "ft-e-p1", "ft-e-p2"]


def _verdict(case_id: str) -> dict | None:
    for suite in SUITES:
        vp = RESULTS / suite / "cases" / case_id / "verdict.json"
        if vp.exists():
            try:
                v = json.loads(vp.read_text(encoding="utf-8"))
                v["_case_dir"] = str(vp.parent)
                return v
            except (OSError, json.JSONDecodeError):
                return None
    return None


def _status(verdict: dict | None) -> str:
    if verdict is None:
        return "not run"
    s = str(verdict.get("status", "fail"))
    if s == "pass":
        return "PASS"
    if s == "declared":
        return "not run"
    return "FAIL"


def _existing_notes(text: str) -> dict[str, str]:
    """Preserve per-case Notes already present in the Master Table (keyed by case id).

    The Class cell may itself contain a pipe (`P/F|D`), so the status literal is
    used as the anchor and everything after it is treated as the note.
    """
    notes: dict[str, str] = {}
    start = text.find("## Scenario Results (Master Table)")
    if start == -1:
        return notes
    end = text.find("\n## ", start + 1)
    section = text[start:end if end != -1 else len(text)]
    for line in section.splitlines():
        m = re.match(
            r"^\|\s*(FT-[A-Z0-9-]+|CUJ-\d+)\s*\|(.*)\|\s*(PASS|FAIL|not run|N/A)\s*\|\s*(.*?)\s*\|\s*$",
            line,
        )
        if m:
            # Unescape the table-safe pipe so re-emitting is idempotent.
            notes[m.group(1)] = m.group(4).replace("\\|", "|")
    return notes


def _fail_evidence(case_id: str, verdict: dict) -> dict[str, str]:
    case_dir = Path(verdict.get("_case_dir", ""))
    failed: list[str] = []
    ap = case_dir / "assertions.ndjson"
    if ap.exists():
        for line in ap.read_text(encoding="utf-8").splitlines():
            try:
                a = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not a.get("ok", False):
                failed.append(str(a.get("name")))
    stderr = ""
    sp = case_dir / "stderr.log"
    if sp.exists():
        stderr = "\n".join(sp.read_text(encoding="utf-8", errors="replace").splitlines()[-12:])
    return {"failed_assertions": ", ".join(failed) or "(none recorded)",
            "case_dir": str(case_dir.relative_to(REPO)), "stderr_tail": stderr}


def _replace_section(text: str, heading: str, body: str) -> str:
    start = text.index(heading) + len(heading)
    nxt = text.find("\n## ", start)
    nxt = len(text) if nxt == -1 else nxt
    return text[:start] + "\n\n" + body.rstrip() + "\n" + text[nxt:]


def main() -> int:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    cases = [c for c in registry if c.get("suite")]
    by_suite: dict[str, list[dict]] = {s: [] for s in SUITES}
    for c in cases:
        by_suite.setdefault(c["suite"], []).append(c)

    rows, fails = [], []
    counts = {"PASS": 0, "FAIL": 0, "not run": 0, "N/A": 0}
    for c in sorted(cases, key=lambda x: x["id"]):
        if c.get("unsupported"):
            # Retired / unsupported: never run, reported as N/A (not a pass/fail).
            counts["N/A"] += 1
            rows.append((c["id"], c["suite"], c.get("class", "P/F"), "N/A"))
            continue
        v = _verdict(c["id"])
        st = _status(v)
        counts[st] += 1
        rows.append((c["id"], c["suite"], c.get("class", "P/F"), st))
        if st == "FAIL":
            fails.append((c, v, _fail_evidence(c["id"], v or {})))

    # --- master table (preserve + emit the per-case Notes column) ---
    text = REPORT.read_text(encoding="utf-8")
    notes = _existing_notes(text)
    table = ["| Case | Suite | Class | Status | Notes |", "|---|---|---|---|---|"]
    for cid, suite, cls, st in rows:
        note = (notes.get(cid, "").strip() or "—").replace("|", "\\|")
        cls_cell = cls.replace("|", "\\|")
        table.append(f"| {cid} | {suite} | {cls_cell} | {st} | {note} |")
    table.append("")
    table.append(f"**Totals:** {counts['PASS']} PASS · {counts['FAIL']} FAIL · "
                 f"{counts['not run']} not run · {counts['N/A']} N/A  (of {len(cases)} field units).")

    # --- per-suite rollup ---
    per = []
    for s in SUITES:
        ids = by_suite.get(s, [])
        cp = cf = cn = cna = 0
        for c in ids:
            if c.get("unsupported"):
                cna += 1
                continue
            st = _status(_verdict(c["id"]))
            if st == "PASS":
                cp += 1
            elif st == "FAIL":
                cf += 1
            elif st == "not run":
                cn += 1
        per.append(f"### {s}\n\n{len(ids)} case(s): {cp} PASS · {cf} FAIL · {cn} not run · {cna} N/A\n")
    per_body = "\n".join(per)

    # --- RCA + defect catalogue (FAILs) ---
    rca, defects = [], ["| Case | Suite | Failed assertions | Evidence |", "|---|---|---|---|"]
    for c, _v, ev in fails:
        rca.append(
            f"### {c['id']} — {c['title']}\n\n"
            f"- **Suite:** {c['suite']} · **Class:** {c.get('class', 'P/F')}\n"
            f"- **Failed assertions:** {ev['failed_assertions']}\n"
            f"- **Evidence:** `{ev['case_dir']}`\n"
            f"- **stderr (tail):**\n\n```\n{ev['stderr_tail']}\n```\n\n"
            f"- **Cause:** TBD (from the evidence above)\n"
            f"- **Fix / regression:** TBD\n"
        )
        defects.append(f"| {c['id']} | {c['suite']} | {ev['failed_assertions']} | `{ev['case_dir']}` |")
    rca_body = "\n".join(rca) or "No failures recorded."
    if not fails:
        defects.append("| — | — | — | — |")

    text = _replace_section(text, "## Scenario Results (Master Table)", "\n".join(table))
    text = _replace_section(text, "## Per-Suite Results", per_body)
    text = _replace_section(text, "## Root Cause Analysis", rca_body)
    text = _replace_section(text, "## Defect Catalogue", "\n".join(defects))
    REPORT.write_text(text, encoding="utf-8")
    print(f"report filled: {counts['PASS']} PASS / {counts['FAIL']} FAIL / "
          f"{counts['not run']} not run / {counts['N/A']} N/A -> {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
