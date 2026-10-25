ft_llm_up
ft_llm_verify
ft_assert "matrix-ag-azure" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_agent.py" ag-azure --llm-out "$FT_LLM_DIR"
ft_assert_llm_capture "matrix-ag-azure-captured"
ft_finalize
