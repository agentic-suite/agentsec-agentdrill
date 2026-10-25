"""AgentDrill wrapper for LlamaIndex - azure-demos shim.

Exposes build_agent(payload=None) that creates a LlamaIndex ReAct agent powered by OMLX.
Based on llamaindex.py pattern.
"""

import os

os.environ.setdefault("OPENAI_API_KEY", "omlx-test")
os.environ.setdefault(
    "OPENAI_BASE_URL",
    os.environ.get("AGENTDRILL_FIELD_ENDPOINT", "http://127.0.0.1:8000/v1"),
)

MODEL = os.environ.get("AGENTDRILL_FIELD_MODEL", "Qwen3.5-4B-4bit")
if MODEL.startswith("openai/"):
    MODEL = MODEL[len("openai/"):]

from llama_index.core import Settings
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.tools import FunctionTool
# OpenAILike accepts an arbitrary model name (a local/oMLX model), unlike
# llama_index.llms.openai.OpenAI which validates against the OpenAI model list.
from llama_index.llms.openai_like import OpenAILike


def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"The weather in {city} is sunny, 72F with a light breeze."


def web_web_search(query: str) -> str:
    """Search the web for information."""
    return f"Search results for: {query}"


def build_agent(payload=None):
    llm = OpenAILike(
        model=MODEL,
        api_base=os.environ["OPENAI_BASE_URL"],
        api_key=os.environ["OPENAI_API_KEY"],
        is_chat_model=True,
        is_function_calling_model=True,
        context_window=32768,
    )

    Settings.llm = llm

    tools = [
        FunctionTool.from_defaults(fn=get_weather),
        FunctionTool.from_defaults(fn=web_web_search),
    ]

    agent = ReActAgent(
        tools=tools,
        llm=llm,
        system_prompt="You are a helpful assistant. You can check the weather and search the web. Keep responses concise.",
    )

    return _SyncReActWrapper(agent)


class _AgentDrillResult:
    """Carrier exposing the workflow result plus the captured tool events.

    The agentdrill llamaindex adapter reads ``agentdrill_tool_calls`` /
    ``agentdrill_tool_results`` (the streamed event history) alongside the
    standard ``response`` / ``structured_response`` / ``raw`` fields.
    """

    def __init__(self, result, tool_calls, tool_results):
        self.result = result
        self.response = getattr(result, "response", None)
        self.structured_response = getattr(result, "structured_response", None)
        self.raw = getattr(result, "raw", None)
        self.sources = getattr(result, "sources", None)
        self.tool_calls = getattr(result, "tool_calls", None)
        self.agentdrill_tool_calls = tool_calls
        self.agentdrill_tool_results = tool_results


class _SyncReActWrapper:
    """Expose a sync ``.chat(user_msg=)`` over the async workflow ReActAgent.

    LlamaIndex's workflow ``ReActAgent.run()`` needs a *running* event loop at
    call time (before the first await). The AgentDrill llamaindex adapter calls
    the agent synchronously, so we drive the async workflow inside a fresh
    event loop here and return a carrier (the result object plus the streamed
    tool events) consumed by the adapter's trajectory/output extraction.
    """

    def __init__(self, agent):
        self._agent = agent

    def chat(self, user_msg: str = ""):
        import asyncio
        from llama_index.core.agent.workflow.workflow_events import (
            AgentStream,
            ToolCall,
            ToolCallResult,
        )
        from llama_index.core.workflow import Context

        async def _drive():
            ctx = Context(self._agent)
            handler = self._agent.run(user_msg, ctx=ctx)
            tool_calls: list = []
            tool_results: list = []
            async for ev in handler.stream_events():
                if isinstance(ev, ToolCall):
                    tool_calls.append(ev)
                elif isinstance(ev, ToolCallResult):
                    tool_results.append(ev)
                elif isinstance(ev, AgentStream):
                    pass
            result = await handler
            return _AgentDrillResult(result, tool_calls, tool_results)

        try:
            return asyncio.run(_drive())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(_drive())
            finally:
                loop.close()
