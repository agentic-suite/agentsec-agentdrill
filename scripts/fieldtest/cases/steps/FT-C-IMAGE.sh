ft_assert "image-validation" "$FT_PY" "$REPO_ROOT/scripts/fieldtest/run_pytest.py" tests/test_docker.py --marker docker
ft_finalize
