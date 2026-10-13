"""``python`` driver (M4 work item 4.3).

Imports a module and calls ``run(payload)``. When ``timeout_seconds`` is set the
callable runs in a separate process, so a hung callable cannot hang the pack.
"""

from __future__ import annotations

import importlib
import multiprocessing
import traceback
from typing import Any

from agentdrill.drivers.base import Driver
from agentdrill.models.errors import AdapterError, AgentTimeoutError, ConfigError


def _load(module: str, function: str) -> Any:
    """Import ``function`` from ``module`` or raise a loud :class:`AdapterError`."""
    try:
        mod = importlib.import_module(module)
    except ImportError as exc:
        raise AdapterError(
            f"python driver cannot import module {module!r}: {exc}"
        ) from exc
    target = getattr(mod, function, None)
    if not callable(target):
        raise AdapterError(
            f"python driver: module {module!r} has no callable {function!r}"
        )
    return target


def _python_child(
    queue: Any, module: str, function: str, payload: dict[str, Any]
) -> None:
    """Child-process entry point: load and call the callable, post the result."""
    try:
        queue.put(("ok", _load(module, function)(payload)))
    except BaseException:  # the traceback is the captured evidence
        queue.put(("error", traceback.format_exc()))


class PythonDriver(Driver):
    """Deliver the attack by calling a Python callable.

    Config keys:

    - ``module`` (required) — import path of the module holding the callable.
    - ``function`` — the callable name (default ``run``).
    - ``timeout_seconds`` — when set, run the callable in a separate process.
    """

    name = "python"

    def _invoke(self, payload: dict[str, Any], config: dict[str, Any]) -> Any:
        module = config.get("module")
        if not isinstance(module, str) or not module:
            raise ConfigError("python driver requires config.module")
        function = str(config.get("function", "run"))
        timeout = config.get("timeout_seconds")
        if timeout is None:
            return _load(module, function)(payload)
        ctx = multiprocessing.get_context("spawn")
        queue: Any = ctx.Queue()
        proc = ctx.Process(
            target=_python_child, args=(queue, module, function, payload), daemon=True
        )
        proc.start()
        proc.join(timeout)
        if proc.is_alive():
            proc.terminate()
            proc.join()
            raise AgentTimeoutError(f"python driver timed out after {timeout}s")
        try:
            kind, value = queue.get(timeout=1.0)
        except Exception as exc:  # a dead child yields no result
            raise AdapterError("python driver produced no result") from exc
        if kind == "ok":
            return value
        raise AdapterError(f"python driver raised:\n{value}")
