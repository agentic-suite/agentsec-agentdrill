ft_assert "lab" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m23_lab.py tests/test_m23_carriers.py tests/test_m23_isolation.py
ft_assert "bypass" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m24_search.py tests/test_m24_routes.py tests/test_m24_minimize.py tests/test_m24_coverage.py
ft_finalize
