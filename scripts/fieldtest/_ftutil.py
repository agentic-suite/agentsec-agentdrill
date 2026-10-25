"""Shared helpers for the field-test drivers.

Drivers run inside the agentdrill SUT container at /ft/scripts/, where
``agentdrill`` is on PATH and the output directory lives at
``/data/agentdrill/.agentdrill``. Each driver is a **fail-closed** script: it
prints ``ok: ...`` on success and exits non-zero on any failure, so a case that
cannot prove its claim fails rather than passing silently.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

OUTPUT_DIR = Path(os.environ.get("AGENTDRILL_OUTPUT_DIR", "/data/agentdrill/.agentdrill"))
RUNS = OUTPUT_DIR / "runs"


def run(cmd: str | list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        cmd, shell=isinstance(cmd, str), capture_output=True, text=True
    )
    if check and proc.returncode != 0:
        sys.stderr.write(proc.stdout + proc.stderr)
        raise SystemExit(f"driver: command failed ({proc.returncode}): {cmd}")
    return proc


def runs() -> list[Path]:
    """Every run directory under the output dir, newest last."""
    if not RUNS.exists():
        return []
    return sorted(p for p in RUNS.iterdir() if p.is_dir())


def latest_run() -> Path | None:
    rs = runs()
    return rs[-1] if rs else None


def run_json() -> dict:
    """The pack-level index (``run.json``) of the newest run, or {}."""
    r = latest_run()
    if r is None:
        return {}
    p = r / "run.json"
    if not p.exists():
        return {}
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return obj if isinstance(obj, dict) else {}


def artifacts() -> list[dict]:
    """Every per-case artifact (``artifacts/<case_id>.json``) of the newest run."""
    r = latest_run()
    if r is None:
        return []
    out: list[dict] = []
    adir = r / "artifacts"
    if not adir.exists():
        return out
    for path in sorted(adir.glob("*.json")):
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(obj, dict):
            out.append(obj)
    return out


def fixture(kind: str) -> Path:
    return Path(f"/ft/fixtures/{kind}")


def arg(argv: list[str], name: str, default: str | None = None) -> str | None:
    if name in argv:
        return argv[argv.index(name) + 1]
    return default


def ok(msg: str) -> None:
    print(f"ok: {msg}")


def fail(msg: str) -> None:
    print(f"fail: {msg}", file=sys.stderr)
    raise SystemExit(1)
