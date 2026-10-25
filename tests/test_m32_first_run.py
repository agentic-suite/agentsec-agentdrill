"""M32 32.2 — timed clean-machine first run.

Runs the bundled offline demo (`agentdrill quickstart`) in a fresh container and
asserts it produces the first honest drill result within the 15-minute budget.
Docker-marked: deselected by the default functional suite, run in the docker
suite / the milestone gate.
"""

from __future__ import annotations

import shutil
import subprocess
import time

import pytest

pytestmark = [pytest.mark.docker, pytest.mark.slow]

IMAGE = "agentdrill-fieldtest:local"
BUDGET_SECONDS = 15 * 60
DOCKER = shutil.which("docker") or "docker"


def _docker_available() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        subprocess.run(  # noqa: S603
            [DOCKER, "info"], capture_output=True, timeout=10, check=True
        )
    except (subprocess.SubprocessError, OSError):
        return False
    return True


@pytest.mark.skipif(not _docker_available(), reason="docker not available")
def test_quickstart_first_run_within_budget() -> None:
    start = time.monotonic()
    proc = subprocess.run(  # noqa: S603
        [DOCKER, "run", "--rm", IMAGE, "agentdrill", "quickstart"],
        capture_output=True,
        text=True,
        timeout=BUDGET_SECONDS + 120,
    )
    elapsed = time.monotonic() - start
    output = proc.stdout + proc.stderr
    assert proc.returncode == 0, output
    assert "outcome:" in output, output
    assert "never evidence" in output, output  # the demo is not evidence
    assert elapsed <= BUDGET_SECONDS, f"first run took {elapsed:.1f}s > {BUDGET_SECONDS}s"
