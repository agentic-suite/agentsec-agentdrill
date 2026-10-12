# agentdrill — build & quality-gate tooling.
#
# `make setup` creates the local virtualenv and installs dev dependencies;
# `lint` / `typecheck` / `test` are the quality gates. Docker- and oMLX-backed
# tests are environment-gated: `test` runs the functional suite, `test-all`
# runs everything.

VENV ?= .venv
PY   := $(VENV)/bin/python
RUFF := $(VENV)/bin/ruff
MYPY := $(VENV)/bin/mypy

.PHONY: setup lint typecheck test test-all cov fmt clean

setup:  ## Create the venv and install dev dependencies.
	uv venv --allow-existing $(VENV)
	uv pip install -e '.[dev]' --python $(PY)

lint:  ## ruff, zero violations.
	$(RUFF) check .

typecheck:  ## mypy --strict.
	$(MYPY)

test:  ## Functional test suite (excludes docker/omlx infra tests).
	$(PY) -m pytest -m "not docker and not omlx"

test-all:  ## Full suite incl. docker/omlx (needs a daemon + oMLX server).
	$(PY) -m pytest

cov:  ## Functional suite with the coverage gate (>=95%).
	$(PY) -m pytest -m "not docker and not omlx" --cov=agentdrill --cov-report=term-missing --cov-fail-under=95

fmt:  ## Auto-format src and tests.
	$(RUFF) format src tests

clean:  ## Remove venv and caches.
	rm -rf $(VENV) .pytest_cache .mypy_cache .ruff_cache
