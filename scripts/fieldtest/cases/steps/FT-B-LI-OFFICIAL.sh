ft_llm_up
ft_llm_verify
ft_assert "matrix-li-official" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_agent.py" li-official --llm-out "$FT_LLM_DIR"
ft_assert_llm_capture "matrix-li-official-captured"
ft_finalize
