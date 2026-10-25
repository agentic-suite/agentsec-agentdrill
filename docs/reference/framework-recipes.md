# Framework Recipes (Tier 2)

**Status:** built (v0.1.0). How Tier-2 agent frameworks are reached — via promptfoo/garak interop
and (later) adapter packs, never a rewrite.

## Approach

agentdrill drills a **deployed stack**, so a framework is reached in one of two ways:

1. **Interop import (v0.1.0):** import a framework's promptfoo/garak/PyRIT suite into an attack pack.
2. **Framework pack (in scope):** a per-framework attack pack that drives the framework's agent loop through
   a driver adapter.

| Framework | Path | Notes |
|---|---|---|
| **LangChain / LangGraph** | interop + driver | agent loop over tools; the org's own stack |
| **CrewAI** | interop + driver | multi-agent; delegation/inter-agent abuse cases |
| **OpenAI Agents SDK** | interop + driver | tool-call trajectory extraction |
| **AutoGen / AG2** | interop + driver | multi-agent chat history |
| **LlamaIndex** | interop + driver | agent runner + tool calls |
| **PydanticAI** | interop + driver | typed tool calls |
| **smolagents** | interop + driver | tool-calling agent mode |

## Recipe skeleton

```sh
agentdrill init --template exfil-chain --name langgraph-exfil
# author cases + oracle; add benign_twin + cleanup
agentdrill pack lint langgraph-exfil.yaml
agentdrill run --pack langgraph-exfil --target ./stack.yaml --sandbox
```

## Fidelity

A framework row is `fixture-verified` until its pack passes against a live loop, then `live-verified`
([compatibility](compatibility.md)). No row claims more than it demonstrates.
