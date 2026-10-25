ft_assert "dry-run-plan" bash -lc '"$FT_PY" -m agentdrill run --dry-run --pack "$REPO_ROOT/packs/incidents-core.yaml" --agent python:my_agent.run 2>/dev/null | grep -q "executions: 0"'
ft_assert "dry-run-cases-listed" bash -lc '"$FT_PY" -m agentdrill run --dry-run --pack "$REPO_ROOT/packs/incidents-core.yaml" --agent python:my_agent.run 2>/dev/null | grep -q "replit-destructive-command"'
ft_assert "dry-run-explain" bash -lc '"$FT_PY" -m agentdrill run --dry-run --explain --pack "$REPO_ROOT/packs/incidents-core.yaml" --agent python:my_agent.run 2>/dev/null | grep -q "because:"'
ft_assert "mcp-readonly" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m20_mcp.py
ft_assert "dry-run-cli-tests" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_cli_dry_run.py
ft_finalize
