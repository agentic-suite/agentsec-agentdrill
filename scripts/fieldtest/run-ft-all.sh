#!/usr/bin/env bash
# Run every field-test suite (sA..sE) and collect results.
# Results land under field-test/<FT_VERSION>/results/<suite>/.
#
#   run-ft-all.sh              # all suites
#   run-ft-all.sh track-c      # just these suites
#
# Build once, keep the stack up across all suites, reset state between cases
# (down -v only for `recycle` cases), and tear down once at the end. STACK_KEEP=0
# is permanent.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export FT_VERSION="${FT_VERSION:-v0.1.0}"
export STACK_KEEP=0
export FT_SHARED_STACK=1
# Child suites share this runner's stack (they must not tear it down).
_OWN_STACK="${FT_STACK_OWNED_BY_PARENT:-0}"
export FT_STACK_OWNED_BY_PARENT=1
# shellcheck source=lib.sh
source "$HERE/lib.sh"
export STACK_ON_NO_DOCKER=fail
ft_build_images || true

ALL=(track-a demos ft-e-p0 ft-e-p1 ft-e-p2 track-c track-b)

suites=("$@")
if [[ ${#suites[@]} -eq 0 ]]; then
  suites=("${ALL[@]}")
fi

echo "==> field-test run: ${#suites[@]} suite(s); STACK_KEEP=$STACK_KEEP; FT_LLM_MODEL=${FT_LLM_MODEL:-unset}"
rc=0
for s in "${suites[@]}"; do
  echo
  echo "############## suite $s ##############"
  if ! bash "$HERE/run-suite.sh" "$s"; then
    echo "!! suite $s had failures" >&2
    rc=1
  fi
done
echo
echo "==> run complete (rc=$rc). Results under field-test/$FT_VERSION/results/"

# One teardown per run — unless a parent runner owns the stack.
if [[ "${_OWN_STACK:-0}" != "1" ]]; then
  stack_teardown
fi

exit "$rc"
