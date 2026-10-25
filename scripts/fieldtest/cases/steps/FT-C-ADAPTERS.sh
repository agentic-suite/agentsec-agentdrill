ft_llm_up
ft_llm_verify
ft_llm_probe "adapters-llm"
export AGENTDRILL_FIELD_OUTPUT_DIR="$FT_CASE_DIR/artifacts"
ft_assert "adapters-llm" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_adapters_adk_llm.py tests/test_adapters_autogen_llm.py tests/test_adapters_llamaindex_llm.py tests/test_adapters_smolagents_llm.py --marker omlx
ft_assert_llm_capture "adapters-llm-captured"
ft_finalize
