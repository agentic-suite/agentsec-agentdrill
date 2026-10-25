ft_assert "self-attack" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m14_evasion_pack.py tests/test_m14_cadence.py
ft_assert "meta-verify" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m14_meta.py tests/test_m14_holdout.py
ft_assert "oracle-credibility" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m19_battery.py tests/test_m19_calibration.py
ft_finalize
