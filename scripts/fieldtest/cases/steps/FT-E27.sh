ft_assert "release-gates" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m21_gate.py tests/test_m21_gaps.py tests/test_m30_standards_claims.py
ft_assert "self-attack-cadence" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m14_cadence.py
ft_finalize
