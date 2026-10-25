ft_assert "schema-verifier" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_schema_version.py tests/test_m18_verifier.py
ft_finalize
