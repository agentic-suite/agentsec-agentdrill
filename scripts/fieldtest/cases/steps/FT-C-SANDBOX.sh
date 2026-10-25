ft_assert "container-sandbox" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_security_container_integration.py --marker docker
ft_finalize
