D="$FT_CASE_DIR/artifacts"
ft_assert "demo-build-bundle" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/make_verify_bundle.py" --out "$D" --name demo
ft_assert "demo-verify-offline" bash -lc '"$FT_PY" -m agentdrill verify "'$D'/demo.json" 2>/dev/null | grep -q "intact:       PASS"'
ft_assert "demo-tamper-caught" bash -lc '"$FT_PY" -m agentdrill verify "'$D'/demo-tampered.json" 2>/dev/null | grep -q "signature does not verify"'
ft_finalize
