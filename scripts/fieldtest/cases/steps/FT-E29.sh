ft_llm_up
ft_llm_verify
ft_llm_probe "judge-parity"
export AGENTDRILL_FIELD_OUTPUT_DIR="$FT_CASE_DIR/artifacts"
ft_assert "judge-parity" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_judge_contract.py
ft_assert_llm_capture "judge-parity-captured"
ft_finalize
