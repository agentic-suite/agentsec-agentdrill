#!/usr/bin/env bash
# Run the whole field-test case set (or a subset). Usage:
#   run-all.sh                 # all cases, in registry order
#   run-all.sh FT-A-QUICKSTART # only these
#
# Results are written once to field-test/<FT_VERSION>/results/<run-id>/.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib.sh
source "$HERE/lib.sh"
export STACK_ON_NO_DOCKER=fail

# Shared stack across cases: built once, kept up, reset in place between cases;
# torn down once at the end (or by the parent). STACK_KEEP=0 is permanent.
export FT_SHARED_STACK=1
export STACK_KEEP=0

# No global Docker gate: each case declares whether it needs Docker (host-native
# cases run without it). A case that cannot run is recorded as a failure, never
# skipped.
export FT_RUN_ID="${FT_RUN_ID:-all}"
ft_run_init
ft_build_images || true

ids=("$@")
if [[ ${#ids[@]} -eq 0 ]]; then
  while IFS= read -r id; do
    ids+=("$id")
  done < <(python3 - "$HERE/cases/registry.json" <<'PY'
import json, sys
try:
    registry = json.load(open(sys.argv[1]))
except (OSError, ValueError):
    registry = []
for case in registry:
    if not case.get("unsupported"):
        print(case["id"])
PY
)
fi

rc=0
for id in "${ids[@]}"; do
  echo
  echo "################ $id ################"
  if ! bash "$HERE/run-case.sh" "$id"; then
    rc=1
  fi
done

echo
echo "==> Aggregating results into $FT_RUN_DIR"
python3 "$HERE/collect-results.py" "$FT_RUN_DIR" --expect "${ids[@]}" || true

# One teardown per run — unless a parent runner owns the stack.
if [[ "${FT_STACK_OWNED_BY_PARENT:-0}" != "1" ]]; then
  stack_teardown
fi

exit "$rc"
