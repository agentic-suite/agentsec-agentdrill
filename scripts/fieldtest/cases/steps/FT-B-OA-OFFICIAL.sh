ft_llm_up
ft_llm_verify
ft_assert "matrix-oa-official" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_agent.py" oa-official --llm-out "$FT_LLM_DIR"
ft_assert_llm_capture "matrix-oa-official-captured"
ft_finalize
