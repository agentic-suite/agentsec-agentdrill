ft_up_sut
ft_assert_sut "quickstart-runs" "agentdrill quickstart > /tmp/qs.txt 2>&1"
ft_assert_sut "quickstart-outcome" "grep -E 'outcome: blocked' /tmp/qs.txt"
ft_assert_sut "quickstart-watermark" "grep -qi 'never evidence' /tmp/qs.txt"
ft_assert_sut "quickstart-attestation" "grep -qi 'attestation:' /tmp/qs.txt"
ft_capture_store
ft_finalize
