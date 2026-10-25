ft_assert "byod" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m25_contract.py tests/test_m25_conformance.py tests/test_m25_head_to_head.py tests/test_m25_neutrality.py tests/test_m25_zoo.py
ft_finalize
