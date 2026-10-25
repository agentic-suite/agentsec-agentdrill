ft_llm_up
ft_llm_verify
ft_assert "matrix-sm-smolcc" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_agent.py" sm-smolcc --llm-out "$FT_LLM_DIR"
ft_assert_llm_capture "matrix-sm-smolcc-captured"
ft_finalize
