ft_assert "baseline-drift" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_baselines.py tests/test_benchmarks.py tests/test_m9_comparison.py tests/test_m9_change_detection.py
ft_finalize
