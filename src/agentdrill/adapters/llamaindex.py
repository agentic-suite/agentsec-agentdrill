"""LlamaIndex adapter: invoke a LlamaIndex agent via Python import.

Imports a user-supplied Python module that exposes a ``build_agent`` function
(or a pre-built agent instance), calls it to obtain an ``AgentRunner``-like
object, and invokes it with ``agent.chat(user_msg=...)`` (async, with a sync
``query`` fallback). The returned ``AgentChatResponse`` is converted to a
standardized run envelope with trajectory steps (tool calls, tool results, and
the final response).

Trajectory is extracted from ``response.sources`` (``ToolOutput`` objects with
``tool_name``, ``raw_input``, ``raw_output``).

Exports:
    LlamaIndexAdapter: Adapter for LlamaIndex-based agents.
"""

from __future__ import annotations

import asyncio
import importlib
import inspect
import json
from typing import Any

from agentdrill.adapters._model_patch import apply_model_patch
from agentdrill.adapters.base import Adapter
from agentdrill.models.errors import AdapterError


class LlamaIndexAdapter(Adapter):
    """Invoke a LlamaIndex agent via Python import.

    Attributes:
        name: Identifier "llamaindex".
    """

    name = "llamaindex"

    def _invoke(self, payload: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
        apply_model_patch()
        module_name = config.get("module")
        if not module_name:
            raise AdapterError("llamaindex adapter requires `module` in config")

        function_name = config.get("function", "build_agent")

        try:
            mod = importlib.import_module(module_name)
        except ImportError as exc:
            raise AdapterError(
                f"cannot import module '{module_name}': {exc}. "
                "If this is a llamaindex agent, install with: "
                "pip install agentdrill[llamaindex]"
            ) from exc

        try:
            builder: Any = getattr(mod, function_name)
        except AttributeError as exc:
            raise AdapterError(
                f"module '{module_name}' has no function '{function_name}'"
            ) from exc

        try:
            if inspect.isfunction(builder) or inspect.ismethod(builder) or inspect.isclass(builder):
                sig = inspect.signature(builder)
                required = [
                    p for p in sig.parameters.values()
                    if p.default is inspect._empty
                    and p.kind in (
                        inspect.Parameter.POSITIONAL_ONLY,
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    )
                ]
                callable_builder: Any = builder
                agent = callable_builder(payload) if required else callable_builder()
            else:
                agent = builder
        except Exception as exc:
            raise AdapterError(f"build_agent failed: {exc}") from exc

        user_input = payload.get("input", "")

        try:
            result = _invoke_agent(agent, user_input)
        except AdapterError:
            raise
        except Exception as exc:
            raise AdapterError(f"agent chat failed: {exc}") from exc

        steps = _extract_trajectory(result)
        final_content, structured = _extract_output(result, steps)
        if final_content and not any(s.get("type") == "response" for s in steps):
            steps.append({
                "type": "response",
                "content": final_content,
                "duration_ms": None,
            })

        return {
            "schema_version": "agentdrill.run_envelope.v1",
            "status": "completed",
            "output": {"final": final_content, "structured": structured},
            "trajectory": {"steps": steps},
            "cost": None,
            "error": None,
        }


def _invoke_agent(agent: Any, user_input: str) -> Any:
    """Invoke a LlamaIndex agent, handling sync, async, and awaitable results.

    LlamaIndex agents come in several flavours:
    - Older ``AgentRunner`` uses sync ``.chat()`` / ``.query()``
    - Newer ``ReActAgent`` (``workflow`` module) has sync ``.run()`` that
      returns a ``WorkflowHandler`` (an ``Awaitable`` but not a coroutine),
      and needs a running event loop to execute.

    This helper detects the right path and runs everything inside
    ``asyncio.run()`` when async semantics are needed.
    """
    if inspect.iscoroutinefunction(getattr(agent, "chat", None)):
        return asyncio.run(agent.chat(user_msg=user_input))
    if hasattr(agent, "chat"):
        result = agent.chat(user_msg=user_input)
        if inspect.isawaitable(result):
            return asyncio.run(_await_result(result))
        return result
    if inspect.iscoroutinefunction(getattr(agent, "run", None)):
        return asyncio.run(agent.run(user_input))
    if hasattr(agent, "run"):
        try:
            result = agent.run(user_msg=user_input)
        except RuntimeError:
            result = asyncio.run(_run_workflow(agent, user_input))
        if inspect.isawaitable(result):
            return asyncio.run(_await_result(result))
        return result
    if hasattr(agent, "query"):
        result = agent.query(user_input)
        if inspect.isawaitable(result):
            return asyncio.run(_await_result(result))
        return result
    raise AdapterError(
        "build_agent must return an object with .chat(), .run(), or .query()"
    )


async def _await_result(result: Any) -> Any:
    """Await an awaitable result (coroutine or WorkflowHandler)."""
    return await result


async def _run_workflow(agent: Any, user_input: str) -> Any:
    """Run a LlamaIndex workflow agent inside an event loop.

    Handles agents whose ``.run()`` method needs a running event loop to
    construct the ``WorkflowHandler``.  Creates a ``Context`` and consumes
    the handler.
    """
    try:
        from llama_index.core.workflow import Context
    except ImportError:
        ctx = None
    else:
        try:
            ctx = Context(agent)
        except Exception:
            ctx = None
    if ctx is not None:
        handler = agent.run(user_input, ctx=ctx)
    else:
        handler = agent.run(user_input)
    # Consume streaming events to ensure the workflow completes
    try:
        async for _ev in handler.stream_events():
            pass
    except Exception:  # noqa: S110
        pass
    return await handler


def _tool_name_of(obj: Any) -> str:
    """Best-effort tool-name extraction from ToolCall-like objects or dicts."""
    if isinstance(obj, dict):
        return str(obj.get("tool_name") or obj.get("name") or "")
    return str(getattr(obj, "tool_name", "") or getattr(obj, "name", "") or "")


def _tool_args_of(obj: Any) -> dict[str, Any]:
    """Best-effort tool-argument extraction from ToolCall-like objects or dicts."""
    if isinstance(obj, dict):
        args = obj.get("tool_kwargs") or obj.get("args") or obj.get("arguments")
    else:
        args = (
            getattr(obj, "tool_kwargs", None)
            or getattr(obj, "args", None)
            or getattr(obj, "arguments", None)
        )
    return args if isinstance(args, dict) else {}


def _message_text(obj: Any) -> str | None:
    """Best-effort extraction of the final answer text from a response object.

    Handles the shapes LlamaIndex agents return across versions: plain ``str``,
    dicts, ``ChatMessage`` (via ``.content`` or ``.blocks``), and objects
    exposing a ``.content`` string.
    """
    if obj is None:
        return None
    if isinstance(obj, str):
        return obj or None
    if isinstance(obj, dict):
        return _message_text(obj.get("content") or obj.get("response") or obj.get("text"))
    content = getattr(obj, "content", None)
    if isinstance(content, str) and content.strip():
        return content
    blocks = getattr(obj, "blocks", None) or []
    texts = [getattr(b, "text", None) for b in blocks]
    texts = [t for t in texts if isinstance(t, str) and t.strip()]
    if texts:
        return "\n".join(texts)
    return None


def _extract_trajectory(result: Any) -> list[dict[str, Any]]:
    """Extract trajectory steps from a LlamaIndex agent result.

    Supports both agent flavours:
    - Older ``AgentRunner``: ``response.sources`` (``ToolOutput`` objects with
      ``tool_name`` / ``raw_input`` / ``raw_output``).
    - Newer workflow ``ReActAgent``: field wrappers drive the workflow and
      attach the streamed ``ToolCall`` / ``ToolCallResult`` events
      (``agentdrill_tool_calls`` / ``agentdrill_tool_results``); the awaited
      ``AgentOutput`` also carries ``tool_calls`` and the raw chat-completion
      payload.
    """
    steps: list[dict[str, Any]] = []

    # Old AgentRunner flavour: response.sources.
    sources = getattr(result, "sources", None) or []
    for source in sources:
        name = getattr(source, "tool_name", "") or ""
        raw_input = getattr(source, "raw_input", None)
        raw_output = getattr(source, "raw_output", None)
        steps.append({
            "type": "tool_call",
            "tool": name,
            "args": raw_input if isinstance(raw_input, dict) else {},
            "duration_ms": None,
        })
        steps.append({
            "type": "tool_result",
            "tool": name,
            "result": raw_output,
            "duration_ms": None,
        })

    # Workflow flavour: wrapper-attached streamed events (full step history).
    for call in getattr(result, "agentdrill_tool_calls", None) or []:
        steps.append({
            "type": "tool_call",
            "tool": _tool_name_of(call),
            "args": _tool_args_of(call),
            "duration_ms": None,
        })
    for res in getattr(result, "agentdrill_tool_results", None) or []:
        if isinstance(res, dict):
            output = res.get("tool_output")
        else:
            output = getattr(res, "tool_output", None)
        steps.append({
            "type": "tool_result",
            "tool": _tool_name_of(res),
            "result": output,
            "duration_ms": None,
        })

    # Workflow flavour: the awaited AgentOutput's own final-step tool calls.
    for call in getattr(result, "tool_calls", None) or []:
        steps.append({
            "type": "tool_call",
            "tool": _tool_name_of(call),
            "args": _tool_args_of(call),
            "duration_ms": None,
        })

    # Workflow flavour: tool calls recorded inside the raw chat-completion payload.
    raw = getattr(result, "raw", None)
    if isinstance(raw, dict):
        for choice in raw.get("choices") or []:
            message = (choice or {}).get("message") or {}
            for tc in message.get("tool_calls") or []:
                fn = (tc or {}).get("function") or {}
                args = fn.get("arguments")
                steps.append({
                    "type": "tool_call",
                    "tool": str(fn.get("name") or (tc or {}).get("type") or ""),
                    "args": args if isinstance(args, dict) else {},
                    "duration_ms": None,
                })
    return steps


def _extract_output(result: Any, steps: list[dict[str, Any]]) -> tuple[str | None, Any]:
    """Extract the final output and structured data from an agent result.

    Handles the old ``AgentChatResponse`` (``.response`` is a ``str``) and the
    workflow ``AgentOutput`` (``.response`` is a ``ChatMessage``).
    """
    response = getattr(result, "response", None)
    text = _message_text(response)
    if text is None:
        # Field wrappers wrap the workflow result in a carrier exposing `.result`.
        inner = getattr(result, "result", None)
        if inner is not None and inner is not result:
            text = _message_text(getattr(inner, "response", None)) or _message_text(inner)
    structured = getattr(result, "structured_response", None)
    if not isinstance(structured, dict):
        structured = None

    if text:
        parsed = _parse_jsonish(text)
        if isinstance(parsed, dict):
            return text, parsed
        return text, structured
    if structured:
        return json.dumps(structured), structured
    for step in reversed(steps):
        if step.get("type") == "response":
            return step.get("content"), None
    return None, None


def _parse_jsonish(value: str) -> Any:
    """Parse a JSON string, returning the original value on failure."""
    import json
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return value
