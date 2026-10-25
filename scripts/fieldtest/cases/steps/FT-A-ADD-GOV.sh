ft_assert "ledger-roe" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m28_ledger.py tests/test_m28_waivers.py tests/test_m28_roe.py tests/test_m28_interlocks.py tests/test_m28_freshness.py tests/test_m28_exports.py
ft_assert "backtest-path" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m27_backtest.py tests/test_m27_shadow.py tests/test_m27_promote.py tests/test_m27_graph.py tests/test_m27_pathstatus.py tests/test_m27_intake.py
ft_finalize
