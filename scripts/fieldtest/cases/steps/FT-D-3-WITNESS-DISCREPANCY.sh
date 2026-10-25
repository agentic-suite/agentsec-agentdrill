ft_assert "witness-discrepancy" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m23_verdict.py -k "discrepancy"
ft_finalize
