ft_llm_up
ft_llm_verify
ft_llm_probe "container-llm"
export AGENTDRILL_FIELD_OUTPUT_DIR="$FT_CASE_DIR/artifacts"
ft_assert "container-llm" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_security_docker_llm.py --marker docker
ft_assert_llm_capture "container-llm-captured"
ft_finalize
