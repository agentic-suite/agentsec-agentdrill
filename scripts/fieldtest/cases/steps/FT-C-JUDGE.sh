ft_llm_up
ft_llm_verify
ft_llm_probe "judge-omlx"
export AGENTDRILL_FIELD_OUTPUT_DIR="$FT_CASE_DIR/artifacts"
ft_assert "judge-omlx" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_judge_omlx_integration.py --marker omlx
ft_assert_llm_capture "judge-omlx-captured"
ft_finalize
