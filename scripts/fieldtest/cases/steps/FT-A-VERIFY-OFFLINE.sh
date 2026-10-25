B="$FT_CASE_DIR/artifacts"
ft_assert "build-bundles" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/make_verify_bundle.py" --out "$B"
ft_assert "verify-good-bundle" bash -lc '"$FT_PY" -m agentdrill verify "'$B'/bundle.json" 2>/dev/null | grep -q "honest-shaped: PASS"'
ft_assert "verify-good-exit0" bash -lc '"$FT_PY" -m agentdrill verify "'$B'/bundle.json" >/dev/null 2>&1'
ft_assert "verify-tampered-fails" bash -lc '"$FT_PY" -m agentdrill verify "'$B'/bundle-tampered.json" 2>/dev/null | grep -q "intact:       FAIL"'
ft_assert "verify-tampered-exit3" bash -lc '! "$FT_PY" -m agentdrill verify "'$B'/bundle-tampered.json" >/dev/null 2>&1'
ft_assert "verify-cli-tests" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_cli_verify.py
ft_finalize
