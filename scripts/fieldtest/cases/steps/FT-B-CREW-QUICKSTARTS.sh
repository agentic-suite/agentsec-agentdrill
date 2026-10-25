ft_llm_up
ft_llm_verify
ft_assert "matrix-crew-quickstarts" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_agent.py" crew-quickstarts --llm-out "$FT_LLM_DIR"
ft_assert_llm_capture "matrix-crew-quickstarts-captured"
ft_finalize
