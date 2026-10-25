ft_llm_up
ft_llm_verify
ft_assert "matrix-sm-qs" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_agent.py" sm-qs --llm-out "$FT_LLM_DIR"
ft_assert_llm_capture "matrix-sm-qs-captured"
ft_finalize
