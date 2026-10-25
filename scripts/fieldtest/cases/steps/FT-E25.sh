ft_record "cross-OS parity battery: macOS host vs Linux SUT container (plan SS5.7)"
ft_assert "parity-host-run" bash -lc '"$FT_PY" "$REPO_ROOT/scripts/fieldtest/parity_probe.py" run --out "$FT_CASE_DIR/artifacts/parity-host.json"'
ft_assert "parity-linux-run" bash -lc 'docker run --rm -v "$REPO_ROOT":/app -w /app -e PYTHONPATH=/app/src -v "$FT_CASE_DIR/artifacts":/out "agentdrill-fieldtest:${FT_TAG:-local}" python scripts/fieldtest/parity_probe.py run --out /out/parity-linux.json'
ft_assert "parity-ge-995" bash -lc '"$FT_PY" "$REPO_ROOT/scripts/fieldtest/parity_probe.py" compare "$FT_CASE_DIR/artifacts/parity-host.json" "$FT_CASE_DIR/artifacts/parity-linux.json" --min 0.995 --report "$FT_CASE_DIR/artifacts/parity-report.json"'
ft_finalize
