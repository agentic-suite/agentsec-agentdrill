"""Attack-harness module used by the python-driver tests (M4 4.3)."""

from __future__ import annotations

from typing import Any


def run(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a run envelope echoing the case id."""
    return {
        "schema_version": "agentdrill.run_envelope.v1",
        "output": {"final": "handled " + str(payload["case_id"])},
        "trajectory": {"steps": [{"type": "response", "content": "ok"}]},
    }


def run_hang(payload: dict[str, Any]) -> dict[str, Any]:
    """Hang forever, so the driver's hard timeout can be exercised."""
    import time

    time.sleep(30)
    return {"output": {"final": "never"}}
