#!/usr/bin/env python3
"""Generate field-test case specs + step scripts from one registry.

Run::

    python3 scripts/fieldtest/gen_cases.py           # generate
    FT_STRICT_STEPS=1 python3 scripts/fieldtest/gen_cases.py   # fail on weak steps

Every case runs and is pass/fail. There is no skip: a case that does not pass
fails (a P/F|D case may resolve to `declared`). Step scripts source ``lib.sh``,
run assertions with ``ft_assert`` / ``ft_assert_sut`` / ``ft_assert_llm_capture``,
and finish with ``ft_finalize`` (which sets ``FT_CASE_STATUS`` to pass only when
every assertion held AND at least one *grounded* check backs the pass — see
``lib.sh`` / ``check_grounding.py``).

Deep verification (must): the generator refuses to emit a step whose assertions
are only plating (import-only / existence-only / json.tool / cannot-fail /
bare-driver). Set ``FT_STRICT_STEPS=1`` to make that a hard failure.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CASES_DIR = HERE / "cases"
STEPS_DIR = CASES_DIR / "steps"

RUN_PYTEST = '"$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py"'
RUN_AGENT = '"$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_agent.py"'


# --- step builders -----------------------------------------------------------
def _pytest(name: str, *files: str, marker: str | None = None, k: str | None = None,
            allow_skip: bool = False) -> str:
    parts = [f'ft_assert "{name}"', RUN_PYTEST, *files]
    if marker:
        parts += ["--marker", marker]
    if k:
        parts += ["-k", f'"{k}"']
    if allow_skip:
        parts += ["--allow-skip"]
    return " ".join(parts) + "\n"


def _declare(reason: str, gate: str) -> str:
    return f'ft_declare "{reason}" "{gate}"\nft_finalize\n'


def _sut(*cmds: tuple[str, str], pre: str = "ft_up_sut\n", capture: bool = False) -> str:
    s = pre
    for name, cmd in cmds:
        s += f'ft_assert_sut "{name}" "{cmd}"\n'
    if capture:
        s += "ft_capture_store\n"
    return s + "ft_finalize\n"


def _llm_pytest(name: str, *files: str, marker: str | None = None, probe: str | None = None) -> str:
    s = "ft_llm_up\nft_llm_verify\n"
    if probe:
        s += f'ft_llm_probe "{probe}"\n'
    # Write the httpx-captured pairs straight into the case artifacts (artifacts/llm).
    s += 'export AGENTDRILL_FIELD_OUTPUT_DIR="$FT_CASE_DIR/artifacts"\n'
    s += _pytest(name, *files, marker=marker)
    s += f'ft_assert_llm_capture "{name}-captured"\n'
    return s + "ft_finalize\n"


def _matrix(slug: str) -> str:
    return (
        "ft_llm_up\nft_llm_verify\n"
        f'ft_assert "matrix-{slug}" {RUN_AGENT} {slug} --llm-out "$FT_LLM_DIR"\n'
        f'ft_assert_llm_capture "matrix-{slug}-captured"\n'
        "ft_finalize\n"
    )


# --- the registry -------------------------------------------------------------
CASES: list[dict[str, str]] = [
    # ===== Track A — CUJ end-to-end suites =====
    {"id": "FT-A-QUICKSTART", "title": "Timed first run ≤15 min (CUJ-24)", "kind": "quickstart",
     "layer": "sut", "llm": "no", "requires": "docker", "prd": "PRD 04 CUJ-24", "class": "P/F",
     "suite": "track-a", "steps": _sut(
         ("quickstart-runs", "agentdrill quickstart > /tmp/qs.txt 2>&1"),
         ("quickstart-outcome", "grep -E 'outcome: blocked' /tmp/qs.txt"),
         ("quickstart-watermark", "grep -qi 'never evidence' /tmp/qs.txt"),
         ("quickstart-attestation", "grep -qi 'attestation:' /tmp/qs.txt"),
         capture=True)},
    {"id": "FT-A-CORE", "title": "Run a pack, gate a PR, reproduce, drill (CUJ-1..4)", "kind": "cuj",
     "layer": "sut", "llm": "no", "requires": "docker", "prd": "PRD 04 CUJ-1..4", "class": "P/F",
     "suite": "track-a",
     "steps": (_sut(
         ("validate-core-pack", "agentdrill validate --pack /ft/scenarios/core-launch.yaml --strict"),
         ("validate-security-pack", "agentdrill validate --pack /ft/scenarios/security-launch.yaml --strict"),
         ("list-packs", "agentdrill list packs >/dev/null"))
         + _pytest("pack-format", "tests/test_attack_pack_loader.py", "tests/test_attack_pack_schema.py")
         + _pytest("ci-gate", "tests/test_m11_gate.py", "tests/test_m11_exit_codes.py")
         + _pytest("benchmark", "tests/test_m10_benchmark.py")
         + "ft_finalize\n")},
    {"id": "FT-A-KILLCHAIN", "title": "Kill-time to probed cessation (CUJ-5/16)", "kind": "cuj",
     "layer": "host", "llm": "no", "requires": "python", "prd": "PRD 04 CUJ-5/16, PRD 18",
     "class": "P/F", "suite": "track-a",
     "steps": _pytest("killchain", "tests/test_m12_timing.py", "tests/test_m12_stages.py",
                      "tests/test_m12_probe.py", "tests/test_m12_findings.py") + "ft_finalize\n"},
    {"id": "FT-A-SELF", "title": "Evasion / meta / holdout / cadence (CUJ-6/25)", "kind": "cuj",
     "layer": "host", "llm": "no", "requires": "python", "prd": "PRD 04 CUJ-6/25, R7", "class": "P/F",
     "suite": "track-a",
     "steps": _pytest("self-attack", "tests/test_m14_evasion_pack.py", "tests/test_m14_cadence.py") +
              _pytest("meta-verify", "tests/test_m14_meta.py", "tests/test_m14_holdout.py") +
              _pytest("oracle-credibility", "tests/test_m19_battery.py", "tests/test_m19_calibration.py") +
              "ft_finalize\n"},
    {"id": "FT-A-LIFECYCLE", "title": "Intake, fix-holds, seams, privacy (CUJ-20..22)", "kind": "cuj",
     "layer": "host", "llm": "no", "requires": "python", "prd": "PRD 04 CUJ-20/21/22, PRD 20",
     "class": "P/F", "suite": "track-a",
     "steps": _pytest("lifecycle", "tests/test_m18_intake.py", "tests/test_m18_fix.py",
                      "tests/test_m18_seams.py", "tests/test_m18_quickstart.py",
                      "tests/test_m18_privacy.py", "tests/test_m18_policy.py") + "ft_finalize\n"},
    {"id": "FT-A-TRUST", "title": "Honest reporting, attribution, severity (CUJ-13/14/19)", "kind": "cuj",
     "layer": "host", "llm": "no", "requires": "python", "prd": "PRD 04 CUJ-13/14/19, PRD 07",
     "class": "P/F", "suite": "track-a",
     "steps": _pytest("honest-report", "tests/test_m10_honest_report.py", "tests/test_m10_stats.py",
                      "tests/test_m10_ci.py", "tests/test_m10_severity.py") +
              _pytest("attribution", "tests/test_m9_attribution.py") + "ft_finalize\n"},
    {"id": "FT-A-SCALE", "title": "Trend, coverage, re-drill, fleet (CUJ-9/10/12/18)", "kind": "cuj",
     "layer": "host", "llm": "no", "requires": "python", "prd": "PRD 04 CUJ-9/10/12/18", "class": "P/F",
     "suite": "track-a",
     "steps": _pytest("trend-heatmap", "tests/test_m10_trends.py", "tests/test_m10_heatmap.py") +
              _pytest("fleet-selection", "tests/test_m20_fleet.py", "tests/test_m11_selection.py",
                      "tests/test_m11_triggers.py") + "ft_finalize\n"},
    {"id": "FT-A-VERIFY-OFFLINE", "title": "Standalone verifier offline (CUJ-23)", "kind": "declare",
     "layer": "host", "llm": "no", "requires": "python", "prd": "PRD 04 CUJ-23, PRD 20 F64",
     "class": "P/F|D", "suite": "track-a",
     "steps": _declare(
         "agentdrill verify CLI is a planned stub (cli/verify.py -> planned()); wiring is plan SS4.5.8",
         "plan SS4.5.8 / CUJ-23")},
    {"id": "FT-A-ADD-PROOF", "title": "Hold@k, honest number, pressure (CUJ-28..31)", "kind": "cuj",
     "layer": "host", "llm": "no", "requires": "python", "prd": "PRD 25/26 CUJ-28..31", "class": "P/F",
     "suite": "track-a",
     "steps": _pytest("pressure", "tests/test_m24_metrics.py", "tests/test_m24_gate.py",
                      "tests/test_m24_pressure.py", "tests/test_m24_tiers.py") +
              _pytest("witness-verdict", "tests/test_m23_verdict.py") + "ft_finalize\n"},
    {"id": "FT-A-ADD-LAB", "title": "Lab carriers + bypass search (CUJ-32..35)", "kind": "cuj",
     "layer": "host", "llm": "no", "requires": "python", "prd": "PRD 27/28 CUJ-32..35", "class": "P/F",
     "suite": "track-a",
     "steps": _pytest("lab", "tests/test_m23_lab.py", "tests/test_m23_carriers.py",
                      "tests/test_m23_isolation.py") +
              _pytest("bypass", "tests/test_m24_search.py", "tests/test_m24_routes.py",
                      "tests/test_m24_minimize.py", "tests/test_m24_coverage.py") + "ft_finalize\n"},
    {"id": "FT-A-ADD-NEUTRAL", "title": "BYOD contract + head-to-head (CUJ-36/37/54/55)", "kind": "cuj",
     "layer": "host", "llm": "no", "requires": "python", "prd": "PRD 29 CUJ-36/37/54/55", "class": "P/F",
     "suite": "track-a",
     "steps": _pytest("byod", "tests/test_m25_contract.py", "tests/test_m25_conformance.py",
                      "tests/test_m25_head_to_head.py", "tests/test_m25_neutrality.py",
                      "tests/test_m25_zoo.py") + "ft_finalize\n"},
    {"id": "FT-A-ADD-GOV", "title": "Ledger, waivers, RoE, attestation (CUJ-38..49)", "kind": "cuj",
     "layer": "host", "llm": "no", "requires": "python", "prd": "PRD 33/34/35 CUJ-38..49",
     "class": "P/F", "suite": "track-a",
     "steps": _pytest("ledger-roe", "tests/test_m28_ledger.py", "tests/test_m28_waivers.py",
                      "tests/test_m28_roe.py", "tests/test_m28_interlocks.py",
                      "tests/test_m28_freshness.py", "tests/test_m28_exports.py") +
              _pytest("backtest-path", "tests/test_m27_backtest.py", "tests/test_m27_shadow.py",
                      "tests/test_m27_promote.py", "tests/test_m27_graph.py",
                      "tests/test_m27_pathstatus.py", "tests/test_m27_intake.py") + "ft_finalize\n"},
    {"id": "FT-A-ADD-DETONATE", "title": "Detonation, Break-It, frontier (CUJ-50..57)", "kind": "cuj",
     "layer": "host", "llm": "no", "requires": "python", "prd": "PRD 36/37/39 CUJ-50..57",
     "class": "P/F", "suite": "track-a",
     "steps": _pytest("detonation-breakit", "tests/test_m29_detonation.py", "tests/test_m29_breakit.py",
                      "tests/test_m29_corpus.py") +
              _pytest("frontier", "tests/test_m29_frontier_identity.py",
                      "tests/test_m29_frontier_approval_memory.py",
                      "tests/test_m29_frontier_browser_multimodal.py",
                      "tests/test_m29_frontier_cascade_wallet.py") + "ft_finalize\n"},
    {"id": "FT-A-ADD-PLATFORM", "title": "Explorer, platform matrix, standards (CUJ-58..63)", "kind": "cuj",
     "layer": "host", "llm": "no", "requires": "python", "prd": "PRD 40/41/42 CUJ-58..63",
     "class": "P/F", "suite": "track-a",
     "steps": _pytest("explorer", "tests/test_m30_explorer_core.py", "tests/test_m30_explorer_analysis.py") +
              _pytest("platform-standards", "tests/test_m30_platform_matrix.py",
                      "tests/test_m30_version_follow.py", "tests/test_m30_standards_claims.py",
                      "tests/test_m30_standards_registry.py", "tests/test_m30_participation.py") +
              "ft_finalize\n"},

    # ===== Required demonstrations =====
    {"id": "FT-D-1-VERIFIER-OFFLINE", "title": "Verifier offline on a clean machine", "kind": "declare",
     "layer": "host", "llm": "no", "requires": "python", "prd": "WBS part 17 SS4.4.1", "class": "P/F|D",
     "suite": "demos",
     "steps": _declare("verify CLI is a planned stub (plan SS4.5.8); run on a clean machine that never "
                       "ran the drill", "plan SS4.4.1")},
    {"id": "FT-D-2-WITNESS-MISSED", "title": "A witness-confirmed missed", "kind": "demo",
     "layer": "host", "llm": "no", "requires": "python", "prd": "WBS part 17 SS4.4.2", "class": "P/F",
     "suite": "demos",
     "steps": _pytest("witness-missed", "tests/test_m23_verdict.py", k="missed") + "ft_finalize\n"},
    {"id": "FT-D-3-WITNESS-DISCREPANCY", "title": "A witness_discrepancy (the log lied)", "kind": "demo",
     "layer": "host", "llm": "no", "requires": "python", "prd": "WBS part 17 SS4.4.3", "class": "P/F",
     "suite": "demos",
     "steps": _pytest("witness-discrepancy", "tests/test_m23_verdict.py", k="discrepancy") + "ft_finalize\n"},
    {"id": "FT-D-4-ROE-ABORT", "title": "The RoE abort, in seconds", "kind": "demo",
     "layer": "host", "llm": "no", "requires": "python", "prd": "WBS part 17 SS4.4.4", "class": "P/F",
     "suite": "demos",
     "steps": _pytest("roe-abort", "tests/test_m28_interlocks.py", k="abort") + "ft_finalize\n"},

    # ===== Track C — docker / LLM infrastructure suites =====
    {"id": "FT-C-IMAGE", "title": "Image builds; CLI works in-container", "kind": "docker",
     "layer": "host", "llm": "no", "requires": "docker", "prd": "PRD 02, plan SS4.3", "class": "P/F",
     "suite": "track-c",
     "steps": _pytest("image-validation", "tests/test_docker.py", marker="docker") + "ft_finalize\n"},
    {"id": "FT-C-CONTAINER-LLM", "title": "Container reaches the host LLM", "kind": "docker_llm",
     "layer": "host", "llm": "yes", "requires": "docker,llm", "prd": "PRD 02, plan SS4.3",
     "class": "P/F", "suite": "track-c",
     "steps": _llm_pytest("container-llm", "tests/test_security_docker_llm.py", marker="docker",
                          probe="container-llm")},
    {"id": "FT-C-SANDBOX", "title": "run_in_container sandbox paths", "kind": "docker",
     "layer": "host", "llm": "no", "requires": "docker", "prd": "PRD 06, plan SS4.3", "class": "P/F",
     "suite": "track-c",
     "steps": _pytest("container-sandbox", "tests/test_security_container_integration.py",
                      marker="docker") + "ft_finalize\n"},
    {"id": "FT-C-JUDGE", "title": "Judge verdicts from the pinned local model", "kind": "docker_llm",
     "layer": "host", "llm": "yes", "requires": "docker,llm", "prd": "PRD 23, plan SS4.3",
     "class": "P/F", "suite": "track-c",
     "steps": _llm_pytest("judge-omlx", "tests/test_judge_omlx_integration.py", marker="omlx",
                          probe="judge-omlx")},
    {"id": "FT-C-ADAPTERS", "title": "Adapters drive a real agent against the endpoint", "kind": "docker_llm",
     "layer": "host", "llm": "yes", "requires": "docker,llm", "prd": "PRD 10, plan SS4.3",
     "class": "P/F", "suite": "track-c",
     "steps": _llm_pytest("adapters-llm", "tests/test_adapters_adk_llm.py",
                          "tests/test_adapters_autogen_llm.py", "tests/test_adapters_llamaindex_llm.py",
                          "tests/test_adapters_smolagents_llm.py", marker="omlx", probe="adapters-llm")},
]

# ===== Track B — agent-harness field matrix (19) =====
_AGENTS = [
    ("lg-azure", "langgraph"), ("lg-official", "langgraph"),
    ("pai-azure", "pydantic-ai"), ("pai-official", "pydantic-ai"),
    ("crew-quickstarts", "crewai"), ("crew-examples", "crewai"), ("crew-qs", "crewai"),
    ("oa-azure", "openai-agents"), ("oa-official", "openai-agents"),
    ("sm-qs", "smolagents"), ("sm-smolcc", "smolagents"), ("sm-deepsearch", "smolagents"),
    ("ag-azure", "autogen"), ("ag-official", "autogen"),
    ("li-azure", "llamaindex"), ("li-official", "llamaindex"),
    ("adk-qs", "adk"), ("adk-sokart", "adk"), ("adk-official", "adk"),
]
for _slug, _fw in _AGENTS:
    CASES.append({
        "id": f"FT-B-{_slug.upper()}", "title": f"Agent matrix: {_slug} ({_fw})", "kind": "matrix",
        "layer": "host", "llm": "yes", "requires": "docker,llm",
        "prd": "PRD 04 Track B, plan SS4.2", "class": "P/F", "suite": "track-b",
        "steps": _matrix(_slug),
    })

# ===== FT-E enrichment =====
CASES += [
    # P0 — gate the report
    {"id": "FT-E01", "title": "Metric coverage: full scorer registry", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E01", "class": "P/F",
     "suite": "ft-e-p0",
     "steps": _pytest("scorers", "tests/test_scoring_registry.py", "tests/test_scoring_engine.py",
                      "tests/test_scoring_deterministic.py", "tests/test_scoring_judge_scorers.py") +
              "ft_finalize\n"},
    {"id": "FT-E02", "title": "Security-eval pack", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E02", "class": "P/F",
     "suite": "ft-e-p0", "steps": _pytest("security-evals", "tests/test_security_evals.py") + "ft_finalize\n"},
    {"id": "FT-E05", "title": "Determinism A/B", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E05", "class": "P/F",
     "suite": "ft-e-p0",
     "steps": _pytest("determinism", "tests/test_determinism.py", "tests/test_m8_reproduction.py",
                      "tests/test_m8_pins.py") + "ft_finalize\n"},
    {"id": "FT-E06", "title": "Judge credibility (battery + canaries + CIs)", "kind": "enrich_llm",
     "layer": "host", "llm": "yes", "requires": "python,llm", "prd": "plan SS4.6 FT-E06", "class": "P/F",
     "suite": "ft-e-p0",
     "steps": _llm_pytest("judge-credibility", "tests/test_m19_battery.py", "tests/test_m19_drift.py",
                          "tests/test_m19_calibration.py", "tests/test_m19_labels.py",
                          probe="judge-credibility")},
    {"id": "FT-E07", "title": "Fault injection (fail-closed)", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E07", "class": "P/F",
     "suite": "ft-e-p0",
     "steps": _pytest("faults", "tests/test_m22_faults.py", "tests/test_attack_runner_errors.py") +
              "ft_finalize\n"},
    {"id": "FT-E08", "title": "Secret-leak sweep", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E08", "class": "P/F",
     "suite": "ft-e-p0", "steps": _pytest("secrets", "tests/test_tools_secrets.py") + "ft_finalize\n"},
    {"id": "FT-E21", "title": "Meta-verification (theater plants caught)", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E21", "class": "P/F",
     "suite": "ft-e-p0",
     "steps": _pytest("meta-verify", "tests/test_m14_meta.py", "tests/test_m14_hidden_case.py") +
              "ft_finalize\n"},
    {"id": "FT-E22", "title": "Publish-gate honesty", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E22", "class": "P/F",
     "suite": "ft-e-p0",
     "steps": _pytest("publish-gate", "tests/test_m10_honest_report.py", "tests/test_m10_stats.py",
                      "tests/test_m10_ci.py") + "ft_finalize\n"},

    # P1 — nightly cadence
    {"id": "FT-E03", "title": "Injection carriers (12 formats)", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E03", "class": "P/F",
     "suite": "ft-e-p1", "steps": _pytest("carriers", "tests/test_m23_carriers.py") + "ft_finalize\n"},
    {"id": "FT-E04", "title": "Reliability (Hold@k / ASR@k)", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E04", "class": "P/F",
     "suite": "ft-e-p1",
     "steps": _pytest("reliability", "tests/test_m24_metrics.py", "tests/test_m24_tiers.py",
                      "tests/test_m24_pressure.py") + "ft_finalize\n"},
    {"id": "FT-E09", "title": "Efficacy control (unguarded twin)", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E09", "class": "P/F",
     "suite": "ft-e-p1",
     "steps": _pytest("efficacy", "tests/test_m13_efficacy.py", "tests/test_m13_inert.py") + "ft_finalize\n"},
    {"id": "FT-E10", "title": "Utility-under-attack", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E10", "class": "P/F",
     "suite": "ft-e-p1",
     "steps": _pytest("utility", "tests/test_m13_utility.py", "tests/test_m13_report.py") + "ft_finalize\n"},
    {"id": "FT-E11", "title": "Baseline drift + change detection", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E11", "class": "P/F",
     "suite": "ft-e-p1",
     "steps": _pytest("baseline-drift", "tests/test_baselines.py", "tests/test_benchmarks.py",
                      "tests/test_m9_comparison.py", "tests/test_m9_change_detection.py") +
              "ft_finalize\n"},
    {"id": "FT-E12", "title": "Schema + verifier round-trip", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E12", "class": "P/F",
     "suite": "ft-e-p1",
     "steps": _pytest("schema-verifier", "tests/test_schema_version.py", "tests/test_m18_verifier.py") +
              "ft_finalize\n"},
    {"id": "FT-E13", "title": "Dark holdout", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E13", "class": "P/F",
     "suite": "ft-e-p1",
     "steps": _pytest("holdout", "tests/test_m14_holdout.py", "tests/test_m14_cadence.py") + "ft_finalize\n"},
    {"id": "FT-E14", "title": "Nightly canary + trend gate", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E14", "class": "P/F",
     "suite": "ft-e-p1",
     "steps": _pytest("canary-trend", "tests/test_m10_trends.py", "tests/test_m30_version_follow.py") +
              "ft_finalize\n"},
    {"id": "FT-E23", "title": "Sandbox egress containment", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E23", "class": "P/F",
     "suite": "ft-e-p1", "steps": _pytest("egress", "tests/test_egress.py") + "ft_finalize\n"},
    {"id": "FT-E24", "title": "Parallel == serial", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E24", "class": "P/F",
     "suite": "ft-e-p1",
     "steps": _pytest("parallel", "tests/test_attack_runner_parallel.py", "tests/test_m22_perf.py") +
              "ft_finalize\n"},
    {"id": "FT-E25", "title": "Cross-OS parity", "kind": "declare",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E25", "class": "P/F|D",
     "suite": "ft-e-p1",
     "steps": _declare("needs a Linux container variant vs the macOS host in one run (plan SS5.7); "
                       "single-host parity is not the measured claim", "plan SS8.4")},
    {"id": "FT-E26", "title": "Interop import field-run", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E26", "class": "P/F",
     "suite": "ft-e-p1",
     "steps": _pytest("interop", "tests/test_m17_interop.py", "tests/test_benchmarks.py") + "ft_finalize\n"},
    {"id": "FT-E27", "title": "Release-shape gates", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E27", "class": "P/F",
     "suite": "ft-e-p1",
     "steps": _pytest("release-gates", "tests/test_m21_gate.py", "tests/test_m21_gaps.py",
                      "tests/test_m30_standards_claims.py") +
              _pytest("self-attack-cadence", "tests/test_m14_cadence.py") + "ft_finalize\n"},
    {"id": "FT-E28", "title": "Dry-run purity + MCP read-only", "kind": "declare",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E28", "class": "P/F|D",
     "suite": "ft-e-p1",
     "steps": _declare("run --dry-run / --explain are documented but unwired (plan SS4.5.9); "
                       "engine exists in dx/dry_run.py", "plan SS4.5.9 / R43")},

    # P2 — scheduled behind P1
    {"id": "FT-E15", "title": "Cost-governor enforcement", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E15", "class": "P/F",
     "suite": "ft-e-p2",
     "steps": _pytest("cost-governor", "tests/test_tools_cost_governor.py", "tests/test_m22_cost.py") +
              "ft_finalize\n"},
    {"id": "FT-E16", "title": "Timeout probing", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E16", "class": "P/F",
     "suite": "ft-e-p2",
     "steps": _pytest("timeout", "tests/test_attack_runner_timeout.py") + "ft_finalize\n"},
    {"id": "FT-E17", "title": "Multi-agent + approval fidelity", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E17", "class": "P/F",
     "suite": "ft-e-p2",
     "steps": _pytest("multiagent-approval", "tests/test_tools_advanced.py") + "ft_finalize\n"},
    {"id": "FT-E18", "title": "Model-matrix tier", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E18", "class": "P/F",
     "suite": "ft-e-p2",
     "steps": _pytest("model-matrix", "tests/test_tools_advanced.py",
                      "tests/test_m30_platform_matrix.py") + "ft_finalize\n"},
    {"id": "FT-E19", "title": "VCR record/replay", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E19", "class": "P/F",
     "suite": "ft-e-p2",
     "steps": _pytest("vcr", "tests/test_fixtures.py", "tests/test_fixtures_integration.py") +
              "ft_finalize\n"},
    {"id": "FT-E20", "title": "Evidence completeness", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E20", "class": "P/F",
     "suite": "ft-e-p2",
     "steps": _pytest("evidence", "tests/test_evidence_binding.py", "tests/test_evidence_artifacts.py",
                      "tests/test_evidence_telemetry.py") + "ft_finalize\n"},
    {"id": "FT-E29", "title": "Judge-backend parity", "kind": "enrich_llm",
     "layer": "host", "llm": "yes", "requires": "python,llm", "prd": "plan SS4.6 FT-E29", "class": "P/F",
     "suite": "ft-e-p2",
     "steps": _llm_pytest("judge-parity", "tests/test_judge_contract.py",
                          probe="judge-parity")},
    {"id": "FT-E30", "title": "Judge-cache correctness", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E30", "class": "P/F",
     "suite": "ft-e-p2",
     "steps": _pytest("judge-cache", "tests/test_cache.py", "tests/test_cache_integration.py") +
              "ft_finalize\n"},
    {"id": "FT-E31", "title": "Plugin discovery", "kind": "enrich",
     "layer": "host", "llm": "no", "requires": "python", "prd": "plan SS4.6 FT-E31", "class": "P/F",
     "suite": "ft-e-p2",
     "steps": _pytest("plugins", "tests/test_plugins.py", "tests/test_pytest_plugin.py") + "ft_finalize\n"},
]


SPEC_TEMPLATE = """# {id} — {title}

**Layer:** {layer} · **LLM:** {llm} · **Requires:** {requires} · **PRD / claim:** {prd} · **Suite:** {suite} · **Class:** {class}

## Goal
{title}. See `docs/field-test/{doc_version}/field-test-plan.md` for the rationale.

## Steps
Run by `cases/steps/{id}.sh` (generated from `gen_cases.py`); every command is
captured to `commands.log`.

## Assertions
The case-specific assertions in `cases/steps/{id}.sh` (each recorded in
`assertions.ndjson`, with the command it ran and a **grounded** flag).
**Pass = every assertion true AND ≥1 grounded check** (`check_grounding.py`).

## LLM capture (must)
An LLM-required case records its request/response pair(s) under
`artifacts/llm/` (sanitized); a pass with no capture fails.

## Artifacts
`field-test/{ft_version}/results/{results_token}/cases/{id}/artifacts/`.

## Cleanup
Shared stack: reset in place between cases; `recycle` cases get a fresh `down -v`
+ boot. The stack is torn down once, at the end of the run.
"""


# --- weak-assertion guard (deep verification) --------------------------------
_WEAK_IMPORT_RE = re.compile(r"python3\s+-c\s+['\"]import ")
_WEAK_DRIVER_RE = re.compile(r"python3\s+/ft/scripts/[\w.-]+\.py")


def _weak_reasons(step: str) -> list[str]:
    """Heuristic catalogue of assertions that prove plumbing, not the property.

    Surfaced so a weak step cannot ship silently; ``FT_STRICT_STEPS=1`` fails
    generation while any remain.
    """
    reasons: list[str] = []
    for line in step.splitlines():
        if "ft_assert" not in line:
            continue
        if _WEAK_IMPORT_RE.search(line):
            reasons.append("import-only")
        if "|| true" in line:
            reasons.append("cannot-fail")
        if "json.tool" in line:
            reasons.append("json.tool")
        if re.search(r"\btest -[fsn]\b", line) and "grep" not in line and "&&" not in line:
            reasons.append("existence-only")
        if _WEAK_DRIVER_RE.search(line) and "grep" not in line and "&&" not in line:
            reasons.append("driver-only(verify-it-asserts)")
    return reasons


_SERVICE_RE = re.compile(r"\b(agentdrill-runner)\b")


def _needs_recycle(step: str) -> bool:
    """A case that touches another service (LLM backend, sandbox runner) is given
    a genuinely fresh stack. Host-native cases never boot the stack."""
    if "ft_up_sut" not in step and "ft_up_all" not in step:
        return False
    return bool(_SERVICE_RE.search(step))


def _slug(title: str) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "-" for ch in title)
    return "-".join(part for part in safe.split("-") if part)[:48]


def _clean_generated() -> None:
    for path in CASES_DIR.glob("*.md"):
        path.unlink()
    for path in STEPS_DIR.glob("*.sh"):
        path.unlink()


def main() -> int:
    CASES_DIR.mkdir(parents=True, exist_ok=True)
    STEPS_DIR.mkdir(parents=True, exist_ok=True)
    _clean_generated()
    for case in CASES:
        step = case["steps"]
        case["recycle"] = _needs_recycle(step)
        slug = _slug(case["title"])
        fields = dict(case)
        fields["doc_version"] = "v0.1.0"
        fields["ft_version"] = "v0.1.0"
        fields["results_token"] = "<run-id>"
        (CASES_DIR / f"{case['id']}-{slug}.md").write_text(
            SPEC_TEMPLATE.format(**fields), encoding="utf-8"
        )
        (STEPS_DIR / f"{case['id']}.sh").write_text(step, encoding="utf-8")
    (CASES_DIR / "registry.json").write_text(json.dumps(CASES, indent=2) + "\n", encoding="utf-8")

    weak = [(c["id"], sorted(set(_weak_reasons(c["steps"])))) for c in CASES if _weak_reasons(c["steps"])]
    if weak:
        print(
            f"gen_cases: WEAK assertions in {len(weak)} case(s) "
            "(import-only / existence-only / cannot-fail / driver-only):"
        )
        for cid, reasons in weak:
            print(f"  {cid}: {', '.join(reasons)}")
        if os.environ.get("FT_STRICT_STEPS") == "1":
            print("gen_cases: FT_STRICT_STEPS=1 -> failing; harden the flagged steps.", file=sys.stderr)
            return 1

    print(f"gen_cases: wrote {len(CASES)} specs + {len(CASES)} step scripts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
