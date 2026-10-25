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

.PHONY: setup lint typecheck test test-all cov fmt clean \
	fieldtest-gen fieldtest-gen-strict fieldtest fieldtest-case fieldtest-suite fieldtest-ft \
	fieldtest-grounding fieldtest-scan fieldtest-persist fieldtest-report fieldtest-clean \
	release-dry-run release-sbom release-verify

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

fieldtest-gen:  ## Regenerate field-test specs + steps from the registry.
	python3 scripts/fieldtest/gen_cases.py

fieldtest-gen-strict:  ## ...and fail if any step is a weak (surface) assertion.
	FT_STRICT_STEPS=1 python3 scripts/fieldtest/gen_cases.py

fieldtest:  ## Run every field-test case (results under field-test/v0.1.0/results/).
	bash scripts/fieldtest/run-all.sh

fieldtest-ft:  ## Run every field-test suite (sA..sE).
	bash scripts/fieldtest/run-ft-all.sh

fieldtest-suite:  ## Run one field-test suite: make fieldtest-suite SUITE=track-c
	@test -n "$(SUITE)" || (echo "usage: make fieldtest-suite SUITE=track-c" >&2 && exit 2)
	bash scripts/fieldtest/run-suite.sh "$(SUITE)"

fieldtest-case:  ## Run one field-test case: make fieldtest-case ID=FT-C-IMAGE
	@test -n "$(ID)" || (echo "usage: make fieldtest-case ID=FT-C-IMAGE" >&2 && exit 2)
	bash scripts/fieldtest/run-case.sh "$(ID)"

fieldtest-grounding:  ## Deep-verification gate: every PASS must be grounded.
	python3 scripts/fieldtest/check_grounding.py

fieldtest-scan:  ## Leak gate: no unmasked secrets in the committed results.
	python3 scripts/fieldtest/scan_results.py

fieldtest-persist:  ## Sanitized results are committed: gates, then stage the evidence.
	python3 scripts/fieldtest/check_grounding.py
	python3 scripts/fieldtest/scan_results.py
	git add field-test/

fieldtest-report:  ## NOTE: the report is hand-maintained (build_report.py is not used).
	@echo "FIELD_TEST_REPORT.md is hand-edited; counts are re-derived from committed verdicts."
	@echo "build_report.py is intentionally not run (it clobbers hand-written findings)."

fieldtest-clean:  ## Remove field-test run artifacts (keeps the results .gitkeep).
	find field-test/v0.1.0/results -mindepth 1 -maxdepth 1 -type d -exec rm -rf {} + 2>/dev/null || true

release-dry-run:  ## M32 32.1 — build + SBOM + checksums + provenance + verify (no publish, no sign).
	$(PY) scripts/release/dry_run.py --dist dist

release-sbom:  ## Generate the CycloneDX SBOM only.
	$(PY) scripts/release/sbom.py --out dist/sbom.cdx.json

release-verify:  ## Re-verify dist/ checksums from disk.
	$(PY) scripts/release/dry_run.py --dist dist --no-build

clean:  ## Remove venv and caches.
	rm -rf $(VENV) .pytest_cache .mypy_cache .ruff_cache dist
