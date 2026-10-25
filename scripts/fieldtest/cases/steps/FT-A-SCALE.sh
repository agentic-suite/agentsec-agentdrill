ft_assert "trend-heatmap" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m10_trends.py tests/test_m10_heatmap.py
ft_assert "fleet-selection" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m20_fleet.py tests/test_m11_selection.py tests/test_m11_triggers.py
ft_finalize
