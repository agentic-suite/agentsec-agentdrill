ft_llm_up
ft_llm_verify
ft_assert "matrix-ag-official" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_agent.py" ag-official --llm-out "$FT_LLM_DIR"
ft_assert_llm_capture "matrix-ag-official-captured"
ft_finalize
