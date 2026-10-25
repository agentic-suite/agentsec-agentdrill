ft_assert "detonation-breakit" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m29_detonation.py tests/test_m29_breakit.py tests/test_m29_corpus.py
ft_assert "frontier" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_m29_frontier_identity.py tests/test_m29_frontier_approval_memory.py tests/test_m29_frontier_browser_multimodal.py tests/test_m29_frontier_cascade_wallet.py
ft_finalize
