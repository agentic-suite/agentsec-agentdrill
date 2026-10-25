ft_llm_up
ft_llm_verify
ft_assert "matrix-crew-qs" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_agent.py" crew-qs --llm-out "$FT_LLM_DIR"
ft_assert_llm_capture "matrix-crew-qs-captured"
ft_finalize
