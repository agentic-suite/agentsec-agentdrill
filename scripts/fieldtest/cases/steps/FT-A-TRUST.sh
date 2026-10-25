ft_assert "honest-report" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m10_honest_report.py tests/test_m10_stats.py tests/test_m10_ci.py tests/test_m10_severity.py
ft_assert "attribution" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m9_attribution.py
ft_finalize
