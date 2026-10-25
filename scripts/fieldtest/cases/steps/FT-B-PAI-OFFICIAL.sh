ft_llm_up
ft_llm_verify
ft_assert "matrix-pai-official" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_agent.py" pai-official --llm-out "$FT_LLM_DIR"
ft_assert_llm_capture "matrix-pai-official-captured"
ft_finalize
