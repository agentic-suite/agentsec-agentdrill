ft_llm_up
ft_llm_verify
ft_llm_probe "judge-credibility"
export AGENTDRILL_FIELD_OUTPUT_DIR="$FT_CASE_DIR/artifacts"
ft_assert "judge-credibility" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m19_battery.py tests/test_m19_drift.py tests/test_m19_calibration.py tests/test_m19_labels.py
ft_assert_llm_capture "judge-credibility-captured"
ft_finalize
