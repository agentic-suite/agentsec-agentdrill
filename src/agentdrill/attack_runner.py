"""Attack-case runner — the execution spine (M3 work items 3.2-3.6).

Loads a validated pack, runs one case or all, captures each case's attack
trajectory, and writes artifacts under ``.agentdrill/runs/<run_id>/``
(``run.json`` + ``artifacts/<case_id>.json``). A case failure never aborts the
pack. Design: ``docs/design/runner.md``.

This module owns the spine only; drivers (M4), oracles/scoring (M6) and evidence
(M7) plug in later.
"""

from __future__ import annotations

import json
import multiprocessing
import time
import traceback
from collections.abc import Callable
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from agentdrill.loading.attack_catalog import pack_ref
from agentdrill.models.artifact import Cost, RunOutput, RunTimestamps, TrajectoryStep
from agentdrill.models.attack_pack import AttackCase, AttackPack
from agentdrill.models.attack_run import CaseArtifact, Run, RunStatus


class CaseOutcome(BaseModel):
    """What a driver returns for one case, before the runner wraps it.

    The runner adds identity, timing and status; the driver supplies the
    observed output, trajectory and cost.
    """

    output: RunOutput = Field(default_factory=RunOutput)
    trajectory: list[TrajectoryStep] = Field(default_factory=list)
    cost: Cost = Field(default_factory=Cost)


#: A driver maps an attack case to the outcome of running it.
DriverFn = Callable[[AttackCase], CaseOutcome]


def _now_iso() -> str:
    """Current UTC time as an ISO-8601 ``Z`` timestamp."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _new_run_id() -> str:
    """A sortable, unique run id."""
    return "run-" + datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")


def _child_entry(queue: Any, driver: DriverFn, case: AttackCase) -> None:
    """Child-process entry point: run the driver and post the outcome.

    Runs at module scope so it is picklable under the ``spawn`` start method.
    """
    try:
        outcome = driver(case)
        queue.put(("ok", outcome.model_dump(mode="json")))
    except BaseException:  # the traceback is the captured evidence
        queue.put(("error", traceback.format_exc()))


class AttackRunner:
    """Run attack cases against a driver and write per-case artifacts.

    Args:
        driver: Callable mapping an :class:`AttackCase` to a :class:`CaseOutcome`.
        runs_dir: Root directory for run artifacts (default ``.agentdrill/runs``).
        timeout_seconds: When set, run each case in a separate process and kill it
            after this many seconds (a hard timeout). When ``None`` the driver runs
            in-process.
        workers: Number of cases to run concurrently (default 1 = serial).
        max_outstanding: Cap on in-flight cases (backpressure); defaults to ``workers``.
        max_cost_usd: Run-level cost cap; once cumulative cost exceeds it the remaining
            cases are ``aborted`` with ``cost_exceeded`` (reported, never hidden).
        driver_manifest: Driver manifest (name + digest) bound into ``run.json`` (M4).
        target_manifest: Target metadata bound into ``run.json`` (M5).
        recon_snapshot: Recon snapshot written to ``recon.json`` and referenced
            from ``run.json`` (M5).
    """

    def __init__(
        self,
        driver: DriverFn,
        *,
        runs_dir: str | Path = ".agentdrill/runs",
        timeout_seconds: float | None = None,
        workers: int = 1,
        max_outstanding: int | None = None,
        max_cost_usd: float | None = None,
        driver_manifest: dict[str, Any] | None = None,
        target_manifest: dict[str, Any] | None = None,
        recon_snapshot: dict[str, Any] | None = None,
    ) -> None:
        self._driver = driver
        self._runs_dir = Path(runs_dir)
        self._timeout_seconds = timeout_seconds
        self._workers = max(1, workers)
        self._max_outstanding = max_outstanding
        self._max_cost_usd = max_cost_usd
        self._driver_manifest = driver_manifest
        self._target_manifest = target_manifest
        self._recon_snapshot = recon_snapshot

    def run_one(self, case: AttackCase, run_id: str) -> CaseArtifact:
        """Run a single case and return its artifact.

        Args:
            case: The attack case to execute.
            run_id: The run this case belongs to (used for the artifact id).

        Returns:
            A :class:`CaseArtifact` with timing and status.
        """
        start_mono = time.perf_counter()
        start = _now_iso()
        outcome, status, error = self._execute(case)
        end = _now_iso()
        duration_ms = int((time.perf_counter() - start_mono) * 1000)
        artifact = CaseArtifact(
            id=f"{run_id}::{case.id}",
            case_id=case.id,
            timestamps=RunTimestamps(start=start, end=end, duration_ms=duration_ms),
            output=outcome.output if outcome is not None else RunOutput(),
            trajectory=outcome.trajectory if outcome is not None else [],
            cost=outcome.cost if outcome is not None else Cost(),
            status=status,
            error=error,
        )
        return self._apply_case_budget(case, artifact)

    @staticmethod
    def _apply_case_budget(case: AttackCase, artifact: CaseArtifact) -> CaseArtifact:
        """Abort a case that exceeded its own ``budget.max_cost_usd``."""
        budget = case.budget
        if (
            budget is not None
            and budget.max_cost_usd is not None
            and artifact.cost.cost_usd > budget.max_cost_usd
        ):
            artifact.status = "aborted"
            artifact.error = "cost_exceeded"
        return artifact

    def _execute(self, case: AttackCase) -> tuple[CaseOutcome | None, RunStatus, str | None]:
        """Run one case, honoring the timeout/isolation policy.

        A driver that raises is captured as ``status="error"`` with its
        traceback — it never propagates to abort the pack.
        """
        if self._timeout_seconds is None:
            try:
                return self._driver(case), "completed", None
            except Exception:  # the traceback is the captured evidence
                return None, "error", traceback.format_exc()
        return self._run_isolated(case)

    def _run_isolated(
        self, case: AttackCase
    ) -> tuple[CaseOutcome | None, RunStatus, str | None]:
        """Run the driver in a separate process with a hard timeout.

        A hung case is terminated and reported as ``timeout`` — it can never
        hang the pack.
        """
        ctx = multiprocessing.get_context("spawn")
        queue: Any = ctx.Queue()
        proc = ctx.Process(target=_child_entry, args=(queue, self._driver, case), daemon=True)
        proc.start()
        proc.join(self._timeout_seconds)
        if proc.is_alive():
            proc.terminate()
            proc.join()
            return None, "timeout", f"case exceeded {self._timeout_seconds}s"
        try:
            kind, payload = queue.get(timeout=1.0)
        except Exception:  # a dead child yields no result
            return None, "error", "driver produced no result"
        if kind == "ok":
            return CaseOutcome.model_validate(payload), "completed", None
        return None, "error", str(payload)

    def run_all(
        self,
        pack: AttackPack,
        *,
        tags: list[str] | None = None,
        run_id: str | None = None,
    ) -> list[CaseArtifact]:
        """Run every case in ``pack`` (optionally tag-filtered) and write artifacts.

        Args:
            pack: A validated attack pack.
            tags: When given, keep only cases carrying at least one of these tags.
            run_id: The run id; generated when omitted.

        Returns:
            The per-case artifacts, in pack order.
        """
        rid = run_id or _new_run_id()
        wanted = set(tags) if tags else None
        cases = [c for c in pack.cases if wanted is None or (wanted & set(c.tags))]
        start_mono = time.perf_counter()
        start = _now_iso()
        if self._max_cost_usd is not None:
            artifacts = self._run_budgeted(cases, rid)
        else:
            artifacts = self._run_cases(cases, rid)
        end = _now_iso()
        duration_ms = int((time.perf_counter() - start_mono) * 1000)
        self._write(
            pack,
            rid,
            artifacts,
            timestamps=RunTimestamps(start=start, end=end, duration_ms=duration_ms),
        )
        return artifacts

    def _run_cases(self, cases: list[AttackCase], run_id: str) -> list[CaseArtifact]:
        """Run ``cases`` serially or concurrently, preserving pack order.

        Concurrency uses a sliding window capped at ``max_outstanding`` (or
        ``workers``) so in-flight work is bounded (backpressure).
        """
        if self._workers <= 1 or len(cases) <= 1:
            return [self.run_one(case, run_id) for case in cases]
        outstanding = max(1, min(self._max_outstanding or self._workers, self._workers))
        results: list[CaseArtifact | None] = [None] * len(cases)
        with ThreadPoolExecutor(max_workers=self._workers) as pool:
            futures: dict[Future[CaseArtifact], int] = {}
            next_index = 0

            def submit() -> None:
                nonlocal next_index
                while next_index < len(cases) and len(futures) < outstanding:
                    futures[pool.submit(self.run_one, cases[next_index], run_id)] = next_index
                    next_index += 1

            submit()
            while futures:
                done, _ = wait(list(futures), return_when=FIRST_COMPLETED)
                for future in done:
                    index = futures.pop(future)
                    results[index] = future.result()
                submit()
        return [artifact for artifact in results if artifact is not None]

    def _run_budgeted(self, cases: list[AttackCase], run_id: str) -> list[CaseArtifact]:
        """Run cases in order under a run-level cost cap.

        Once cumulative cost exceeds ``max_cost_usd`` the remaining cases are
        ``aborted`` with ``cost_exceeded`` (reported, never hidden). The governor
        is inherently sequential.
        """
        artifacts: list[CaseArtifact] = []
        spent = 0.0
        for case in cases:
            if self._max_cost_usd is not None and spent > self._max_cost_usd:
                artifacts.append(self._aborted_case(case, run_id, "cost_exceeded"))
                continue
            artifact = self.run_one(case, run_id)
            artifacts.append(artifact)
            spent += artifact.cost.cost_usd
        return artifacts

    def _aborted_case(self, case: AttackCase, run_id: str, reason: str) -> CaseArtifact:
        """Build an ``aborted`` artifact for a case that was not run."""
        now = _now_iso()
        return CaseArtifact(
            id=f"{run_id}::{case.id}",
            case_id=case.id,
            timestamps=RunTimestamps(start=now, end=now, duration_ms=0),
            status="aborted",
            error=reason,
        )

    def _write(
        self,
        pack: AttackPack,
        run_id: str,
        artifacts: list[CaseArtifact],
        *,
        timestamps: RunTimestamps,
    ) -> None:
        """Write ``run.json`` and ``artifacts/<case_id>.json`` under the run dir."""
        run_dir = self._runs_dir / run_id
        (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)
        run = Run(
            run_id=run_id,
            pack_ref=pack_ref(pack),
            target=self._target_manifest or {},
            driver=self._driver_manifest or {},
            recon_ref="recon.json" if self._recon_snapshot is not None else None,
            timestamps=timestamps,
            case_order=[a.case_id for a in artifacts],
        )
        (run_dir / "run.json").write_text(
            run.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )
        if self._recon_snapshot is not None:
            (run_dir / "recon.json").write_text(
                json.dumps(self._recon_snapshot, indent=2) + "\n", encoding="utf-8"
            )
        for artifact in artifacts:
            (run_dir / "artifacts" / f"{artifact.case_id}.json").write_text(
                artifact.model_dump_json(indent=2) + "\n", encoding="utf-8"
            )
