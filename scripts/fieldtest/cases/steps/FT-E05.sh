ft_assert "determinism" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_determinism.py tests/test_m8_reproduction.py tests/test_m8_pins.py
ft_finalize
