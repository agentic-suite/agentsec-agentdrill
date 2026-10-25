ft_llm_up
ft_llm_verify
ft_assert "matrix-crew-examples" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_agent.py" crew-examples --llm-out "$FT_LLM_DIR"
ft_assert_llm_capture "matrix-crew-examples-captured"
ft_finalize
