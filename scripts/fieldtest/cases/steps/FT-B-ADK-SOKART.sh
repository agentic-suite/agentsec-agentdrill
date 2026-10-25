ft_llm_up
ft_llm_verify
ft_assert "matrix-adk-sokart" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_agent.py" adk-sokart --llm-out "$FT_LLM_DIR"
ft_assert_llm_capture "matrix-adk-sokart-captured"
ft_finalize
