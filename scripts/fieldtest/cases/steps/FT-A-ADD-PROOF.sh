ft_assert "pressure" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m24_metrics.py tests/test_m24_gate.py tests/test_m24_pressure.py tests/test_m24_tiers.py
ft_assert "witness-verdict" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m23_verdict.py
ft_finalize
