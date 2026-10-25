ft_assert "witness-missed" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m23_verdict.py -k "missed"
ft_finalize
