# agentdrill field-test image — the system under test.
#
# Builds from the repo root so it can install the package:
#   docker compose -f scripts/fieldtest/docker-compose.fieldtest.yml build agentdrill
FROM python:3.11-slim

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# git: the field agent matrix clones third-party repos; curl: readiness/log
# helpers; procps for pkill/ps; ca-certificates for TLS.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git curl procps ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

WORKDIR /work

# Install agentdrill (CLI + SDK). Extras: dev (pytest), judge (openai/anthropic
# clients) and the framework adapters the field matrix drives.
COPY pyproject.toml README.md /work/
COPY src /work/src
RUN uv pip install --system --no-cache-dir \
        ".[dev,judge,langgraph,pydanticai,crewai,openai-agents,smolagents,autogen,llamaindex,adk]"

# Field-test definitions + harness helpers (also bind-mounted at runtime).
COPY packs /work/packs
COPY scenarios /work/scenarios
COPY scripts/fieldtest /work/fieldtest/scripts

RUN mkdir -p /data/agentdrill/.agentdrill

CMD ["sleep", "infinity"]
