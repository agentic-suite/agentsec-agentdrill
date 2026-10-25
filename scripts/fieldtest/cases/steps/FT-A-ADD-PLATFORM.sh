ft_assert "explorer" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m30_explorer_core.py tests/test_m30_explorer_analysis.py
ft_assert "platform-standards" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m30_platform_matrix.py tests/test_m30_version_follow.py tests/test_m30_standards_claims.py tests/test_m30_standards_registry.py tests/test_m30_participation.py
ft_finalize
