"""``agentdrill validate`` — validate packs, agents, and baselines for correctness.

Pre-flight validation that catches issues early, before a full evaluation run.
Can validate any combination of:

- **Scenario packs**: structural validity, duplicate IDs, known metric names,
  threshold ranges, YAML/JSON parseability.
- **Agent specs**: adapter type recognition, module importability.
- **Baselines**: file existence, version compatibility with the current pack.
- **Fixture coverage**: checks that every tool used in scenarios has a
  corresponding fixture file in ``scenarios/fixtures/``.

All core library imports are deferred to function scope so this command
loads instantly for ``--help``.
"""

from __future__ import annotations

from pathlib import Path

import click

from agentdrill.cli.util import parse_agent_spec


@click.command()
@click.option(
    "--pack",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to a scenario pack YAML/JSON file to validate",
)
@click.option(
    "--agent",
    help="Agent spec to validate (e.g. 'python:my_module.run' or './my_agent')",
)
@click.option("--baseline", help="Baseline name to validate")
@click.option(
    "--strict",
    is_flag=True,
    help="Promote warnings to errors (e.g. pack version mismatch -> exit 1)",
)
@click.option(
    "--check-fixtures",
    is_flag=True,
    help="Validate that fixture data covers all tools referenced in scenarios",
)
@click.option(
    "--output-dir",
    default=".agentdrill",
    show_default=True,
    help="Output directory for baseline store (used with --baseline)",
)
@click.option(
    "--output-format",
    type=click.Choice(["json", "markdown", "terminal", "github-actions"]),
    default="terminal",
    show_default=True,
)
@click.option(
    "--pre-flight",
    is_flag=True,
    help="Run all validation checks (pack + agent + baseline + fixtures) in one pass",
)
def validate(
    pack: str | None,
    agent: str | None,
    baseline: str | None,
    strict: bool,
    check_fixtures: bool,
    output_dir: str,
    output_format: str,
    pre_flight: bool = False,
) -> None:
    """Validate packs, agents, and baselines for correctness.

    Provide at least one of ``--pack``, ``--agent``, ``--baseline``,
    or ``--check-fixtures``. Multiple flags can be combined to validate
    everything in one pass.

    Args:
        pack: Path to a scenario pack file.
        agent: Agent spec string to validate.
        baseline: Baseline name to validate.
        strict: Promote warnings to errors.
        check_fixtures: Validate fixture coverage for all referenced tools.
        output_dir: Base output directory (for baseline store lookup).
        output_format: Output rendering format.
        pre_flight: Run all applicable checks automatically.

    Exits with:
        0 if all validations pass, 1 otherwise (or 0 with warnings
        unless --strict is set).
    """
    # Core imports deferred for fast --help
    from agentdrill.adapters.factory import create_adapter
    from agentdrill.baselines.store import BaselineStore
    from agentdrill.cli.exit_codes import ExitCode
    from agentdrill.cli.formatter import OutputFormatter
    from agentdrill.loading.attack_catalog import case_tools, missing_fixtures
    from agentdrill.loading.attack_pack_loader import (
        discover_attack_packs,
        is_attack_pack,
        load_attack_pack,
    )
    from agentdrill.loading.pack_loader import load_pack
    from agentdrill.models.errors import ConfigError, PackParseError

    if pre_flight:
        # Auto-discover defaults when running pre-flight checks
        if not pack:
            default_pack = "scenarios/core-launch.yaml"
            if Path(default_pack).exists():
                pack = default_pack
        if not check_fixtures and Path("scenarios/fixtures").exists():
            check_fixtures = True

    results: dict[str, dict[str, object]] = {}
    all_valid = True
    exit_code = int(ExitCode.MISS)

    # Validate pack: attack packs (cases[]) and scenario packs (scenarios[])
    if pack:
        is_attack = is_attack_pack(pack)
        try:
            if is_attack:
                attack_pack = load_attack_pack(pack)
                tag_count = len({t for c in attack_pack.cases for t in c.tags})
                results["pack"] = {
                    "valid": True,
                    "message": (
                        f"Pack '{attack_pack.pack.name}' v{attack_pack.pack.version}:"
                        f" {len(attack_pack.cases)} cases, {tag_count} unique tags"
                    ),
                    "name": attack_pack.pack.name,
                    "version": attack_pack.pack.version,
                    "scenarios": len(attack_pack.cases),
                    "tags": tag_count,
                    "trust": attack_pack.pack.trust,
                }
            else:
                scenario_pack = load_pack(pack)
                meta = scenario_pack.pack
                scenario_count = len(scenario_pack.scenarios)
                tag_count = (
                    len({t for s in scenario_pack.scenarios for t in s.tags})
                    if scenario_pack.scenarios
                    else 0
                )
                results["pack"] = {
                    "valid": True,
                    "message": (
                        f"Pack '{meta.name}' v{meta.version}:"
                        f" {scenario_count} scenarios, {tag_count} unique tags"
                    ),
                    "name": meta.name,
                    "version": meta.version,
                    "scenarios": scenario_count,
                    "tags": tag_count,
                    "trust": meta.trust,
                }
        except (PackParseError, ConfigError) as e:
            results["pack"] = {"valid": False, "message": str(e)}
            all_valid = False
            if is_attack:
                exit_code = int(ExitCode.CONFIG_ERROR)
        except Exception as e:
            results["pack"] = {"valid": False, "message": str(e)}
            all_valid = False

    # Validate the attack-pack catalog during pre-flight when one is present
    if pre_flight and Path("packs").is_dir():
        try:
            catalog = discover_attack_packs(["packs"])
            results["catalog"] = {
                "valid": True,
                "message": (
                    f"{len(catalog)} attack packs,"
                    f" {sum(len(p.cases) for p in catalog)} cases"
                ),
            }
        except (PackParseError, ConfigError) as e:
            results["catalog"] = {"valid": False, "message": str(e)}
            all_valid = False
            exit_code = int(ExitCode.CONFIG_ERROR)

    # Validate agent spec: adapter type recognition + module importability
    if agent:
        try:
            import importlib

            cfg = parse_agent_spec(agent)
            # For framework adapters, verify the module can be imported
            if cfg["type"] in ("python", "langgraph", "pydantic-ai"):
                importlib.import_module(cfg["module"])
            # Verifies the adapter class can be instantiated
            create_adapter(cfg)
            agent_warnings: list[str] = []
            if cfg["type"] == "http":
                import httpx

                try:
                    r = httpx.head(cfg.get("url", ""), timeout=5)
                    if r.status_code >= 500:
                        agent_warnings.append(
                            f"HTTP endpoint returned {r.status_code}"
                        )
                except Exception as e:
                    agent_warnings.append(f"HTTP connectivity check failed: {e}")
            results["agent"] = {
                "valid": True,
                "message": f"Adapter '{cfg['type']}' created successfully",
                "type": cfg["type"],
                "warnings": agent_warnings,
            }
        except Exception as e:
            results["agent"] = {"valid": False, "message": str(e)}
            all_valid = False

    # Enforce trust policy when both pack and agent are provided
    if results.get("pack", {}).get("valid") and results.get("agent", {}).get("valid"):
        from agentdrill.security.policy import TrustLevel, TrustPolicy
        pack_raw = results["pack"].get("trust", "local")
        # mypy complains about assigning str to TrustLevel (Literal[...]), but
        # the runtime check below handles the fallback. The type: ignore is
        # intentional and safe — at runtime pack_trust is always a valid literal
        # after the isinstance guard.
        pack_trust: TrustLevel = pack_raw  # type: ignore[assignment]
        if not isinstance(pack_raw, str) or pack_raw not in ("builtin", "local", "external"):
            pack_trust = "local"
        agent_raw = results["agent"].get("type", "subprocess")
        agent_type: str = agent_raw if isinstance(agent_raw, str) else "subprocess"
        sandbox = False
        policy = TrustPolicy(trust=pack_trust, adapter_type=agent_type, sandbox=sandbox)
        allowed, reason = policy.allowed()
        if not allowed:
            results.setdefault("trust_policy", {})["valid"] = False
            results["trust_policy"]["message"] = reason
            all_valid = False

    # Validate baseline: file exists, version compatibility with pack
    if baseline:
        try:
            store = BaselineStore(base_dir=f"{output_dir}/baselines")
            bl = store.load(baseline)
            warnings: list[str] = []
            if pack:
                pack_meta = load_pack(pack).pack
                if bl.pack != pack_meta.name:
                    warnings.append(
                        f"pack name mismatch:"
                        f" baseline='{bl.pack}' vs pack='{pack_meta.name}'",
                    )
                if bl.pack_version != pack_meta.version:
                    warnings.append(
                        f"pack version mismatch:"
                        f" baseline='{bl.pack_version}' vs pack='{pack_meta.version}'",
                    )
            results["baseline"] = {
                "valid": len(warnings) == 0 or not strict,
                "message": (
                    f"Baseline '{bl.name}':"
                    f" {len(bl.runs)} scenarios, pack={bl.pack} v{bl.pack_version}"
                ),
                "name": bl.name,
                "pack": bl.pack,
                "pack_version": bl.pack_version,
                "runs": len(bl.runs),
                "warnings": warnings,
            }
            if strict and warnings:
                all_valid = False
        except Exception as e:
            results["baseline"] = {"valid": False, "message": str(e)}
            all_valid = False

    # Validate fixture coverage: every tool the pack uses has a fixture file
    if check_fixtures and pack:
        try:
            if is_attack_pack(pack):
                attack_pack = load_attack_pack(pack)
                tools = case_tools(attack_pack)
                missing = missing_fixtures(attack_pack)
                results["fixtures"] = {
                    "valid": len(missing) == 0,
                    "message": (
                        f"{len(missing)} tools missing fixtures"
                        if missing
                        else f"All {len(tools)} tool fixtures present"
                    ),
                    "required_tools": len(tools),
                    "missing": sorted(missing),
                }
            else:
                scenario_pack = load_pack(pack)
                required_tools = {
                    t.name for s in scenario_pack.scenarios for t in s.allowed_tools
                }

                fixtures_dir = Path("scenarios/fixtures")
                available_files = (
                    {f.stem for f in fixtures_dir.glob("*.json")}
                    if fixtures_dir.exists()
                    else set()
                )
                missing = required_tools - available_files
                results["fixtures"] = {
                    "valid": len(missing) == 0,
                    "message": (
                        f"{len(available_files)} fixture files found,"
                        f" {len(missing)} tools missing fixtures"
                        if missing
                        else f"All {len(required_tools)} tool fixtures present"
                    ),
                    "required_tools": len(required_tools),
                    "available_fixtures": len(available_files),
                    "missing": list(missing),
                }
            if missing:
                all_valid = False
        except Exception as e:
            results["fixtures"] = {"valid": False, "message": str(e)}
            all_valid = False

    # No validation targets provided — show usage hint
    if not results:
        click.echo(
            "Nothing to validate."
            " Provide at least one of: --pack, --agent, --baseline, --check-fixtures",
        )
        raise SystemExit(1)

    # Render results and exit with appropriate code
    formatter = OutputFormatter(output_format)
    formatter.format_validation(results)

    if not all_valid:
        raise SystemExit(exit_code)
