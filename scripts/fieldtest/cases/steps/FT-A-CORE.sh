ft_up_sut
ft_assert_sut "validate-core-pack" "agentdrill validate --pack /ft/scenarios/core-launch.yaml --strict"
ft_assert_sut "validate-security-pack" "agentdrill validate --pack /ft/scenarios/security-launch.yaml --strict"
ft_assert_sut "list-packs" "agentdrill list packs >/dev/null"
ft_finalize
ft_assert "pack-format" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_attack_pack_loader.py tests/test_attack_pack_schema.py
ft_assert "ci-gate" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m11_gating.py tests/test_m11_exit_codes.py
ft_assert "benchmark" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m10_benchmark.py
ft_finalize
