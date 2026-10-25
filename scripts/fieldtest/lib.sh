#!/usr/bin/env bash
# Field-test helpers — a thin layer over scripts/stack_lib.sh.
#
# Reuses the repo's stack lifecycle primitive (stack_up / stack_verify /
# stack_teardown_on_exit) and adds per-case result capture. Results are written
# to field-test/<FT_VERSION>/results/<run-id>/ (see
# docs/field-test/v0.1.0/field-test-plan.md).
#
# Source from a runner:
#   source "$(dirname "$0")/lib.sh"
#   ft_require_docker || { ... fail ... }
#   trap ft_teardown_on_exit EXIT
#   ft_case_begin "$ID"
#   ... steps + ft_assert ...
#   ft_finalize
#   ft_case_end "$ID" "$FT_CASE_STATUS"
#
# No skips: every case runs and is pass/fail (or `declared` for a P/F|D case
# whose environment is genuinely unavailable — never a silent pass).
set -euo pipefail

FT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"      # scripts/fieldtest
REPO_ROOT="$(cd "$FT_DIR/../.." && pwd)"                    # repo root
# Load the field-test env file if present (LLM endpoint/model, STACK_*, FT_TAG).
if [[ -f "$FT_DIR/.env" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "$FT_DIR/.env"
  set +a
fi
# Results are version-scoped: field-test/<FT_VERSION>/results/<run-id>/.
# agentdrill's active field-test version is v0.1.0; FT_RESULTS_ROOT overrides the
# whole path when set.
FT_VERSION="${FT_VERSION:-v0.1.0}"
# FREEZE GUARD: a version listed in FT_FROZEN_VERSIONS must never be written by a
# later run (protects a published report's results forever). Empty by default.
for _frozen in ${FT_FROZEN_VERSIONS:-}; do
  if [[ "${FT_VERSION}" == "${_frozen}" && "${FT_ALLOW_FROZEN_WRITE:-0}" != "1" ]]; then
    echo "FATAL: refusing to write to field-test/${_frozen} (frozen). Set FT_VERSION to a later version." >&2
    echo "       (override only with FT_ALLOW_FROZEN_WRITE=1, and only to regenerate that report)" >&2
    exit 3
  fi
done
RESULTS_ROOT="${FT_RESULTS_ROOT:-$REPO_ROOT/field-test/$FT_VERSION/results}"
# Stable run directory name (no timestamps). Override with FT_RUN_ID=... per step.
FT_RUN_ID="${FT_RUN_ID:-all}"
FT_RUN_DIR="$RESULTS_ROOT/$FT_RUN_ID"

# shellcheck source=../stack_lib.sh
source "$REPO_ROOT/scripts/stack_lib.sh"

# Prefer the repo venv's python so host-native pytest cases work out of the box
# (override with AGENTDRILL_PYTHON).
if [[ -x "$REPO_ROOT/.venv/bin/python" ]]; then
  FT_PY="${AGENTDRILL_PYTHON:-$REPO_ROOT/.venv/bin/python}"
else
  FT_PY="${AGENTDRILL_PYTHON:-python3}"
fi
export FT_PY

# The field-test compose overlay. agentdrill has no base compose stack, so the
# overlay is the whole stack: the agentdrill CLI/SDK (system under test). There is
# no LLM container — the LLM is the host oMLX server (see FT_LLM_HOST_URL / FT_LLM_BASE_URL).
# --project-directory pins relative build contexts / mounts to the repo root
# (the overlay lives in scripts/fieldtest/, so without it `context: .` would
# resolve to that subdirectory).
STACK_COMPOSE=(docker compose --project-directory "$REPO_ROOT" -f "$FT_DIR/docker-compose.fieldtest.yml")
FT_SUT_SERVICE="agentdrill"
FT_SERVICES=(agentdrill)
STACK_SERVICES=(agentdrill)
# The LLM is the local oMLX server on the host (OpenAI-compatible), reached from
# the container via host.docker.internal. There is no LLM container. Variables are
# namespaced FT_LLM_* so the ambient environment (e.g. a coding agent's
# OPENAI_*/LLM_* vars) can never leak into a field-test LLM call.
FT_LLM_HOST_URL="${FT_LLM_HOST_URL:-http://127.0.0.1:8000}"
FT_LLM_BASE_URL="${FT_LLM_BASE_URL:-http://host.docker.internal:8000/v1}"
FT_LLM_MODEL="${FT_LLM_MODEL:-Qwen3.5-4B-4bit}"
FT_JUDGE_MODEL="${FT_JUDGE_MODEL:-Qwen3.5-9B-MLX-4bit}"
export FT_LLM_HOST_URL FT_LLM_BASE_URL FT_LLM_MODEL FT_JUDGE_MODEL

FT_CASE_DIR=""
FT_CASE_STATUS="fail"
FT_ASSERT_FAILED=0
# Declare class: FT_CASE_CLASS is "P/F" or "P/F|D" (from the registry);
# FT_CASE_DECLARED / FT_DECLARE_LIMITATION / FT_DECLARE_GATE are set by ft_declare.
FT_CASE_CLASS="${FT_CASE_CLASS:-P/F}"
FT_CASE_DECLARED=0
FT_DECLARE_LIMITATION=""
FT_DECLARE_GATE=""

# --- docker gate -------------------------------------------------------------
# Overrides stack_lib's stack_require_docker, which exits 0 on a missing daemon
# (a false green for a field test). This returns non-zero so the runner records
# a hard failure: a case that cannot run is a failed case, never a skip.
ft_require_docker() {
  if ! docker info >/dev/null 2>&1; then
    echo "FAIL: Docker is unavailable; field test cannot run." >&2
    return 3
  fi
}

# --- run directory -----------------------------------------------------------
ft_run_init() {
  mkdir -p "$FT_RUN_DIR"
  if [[ ! -f "$FT_RUN_DIR/env.json" ]]; then
    {
      printf '{"run_id":"%s","version":"%s","docker":"%s","compose":"%s","os":"%s","arch":"%s","llm_base_url":"%s","llm_model":"%s","judge_model":"%s"}\n' \
        "$FT_RUN_ID" \
        "$FT_VERSION" \
        "$(docker --version 2>/dev/null || echo unknown)" \
        "$(docker compose version --short 2>/dev/null || echo unknown)" \
        "$(uname -s 2>/dev/null || echo unknown)" \
        "$(uname -m 2>/dev/null || echo unknown)" \
        "${FT_LLM_BASE_URL}" \
        "${FT_LLM_MODEL}" \
        "${FT_JUDGE_MODEL}"
    } > "$FT_RUN_DIR/env.json"
  fi
}

# --- setup log (preserved) ---------------------------------------------------
# The stack setup/readiness transcript is written to a *preserved* log under the
# version-scoped results root (committed with the run), so a reviewer can see
# exactly what came online and when.
FT_SETUP_DIR="${FT_SETUP_DIR:-$RESULTS_ROOT/_setup}"
FT_SETUP_LOG="${FT_SETUP_LOG:-$FT_SETUP_DIR/${FT_RUN_ID}-stack-up.log}"

_ft_log() {
  mkdir -p "$(dirname "$FT_SETUP_LOG")"
  printf '[%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" | tee -a "$FT_SETUP_LOG"
}

# Confirm the stack is genuinely ONLINE (not merely "container started"):
#   1. every expected service has a running container,
#   2. every service that declares a healthcheck is `healthy`,
#   3. the SUT answers (`agentdrill version`), and
#   4. when the LLM is required, its endpoint responds.
# Returns non-zero (loudly) on timeout — a stack that never comes up must never
# be reported as "up". The whole transcript is preserved in $FT_SETUP_LOG.
ft_wait_ready() {
  local timeout="${STACK_TIMEOUT:-180}"
  local deadline=$((SECONDS + timeout))
  _ft_log "waiting for stack readiness (timeout ${timeout}s)"

  # 1 + 2: running + healthy
  while :; do
    local all_ok=1 svc cid status health
    while IFS= read -r svc; do
      cid="$("${STACK_COMPOSE[@]}" ps -q "$svc" 2>/dev/null)"
      if [[ -z "$cid" ]]; then _ft_log "  $svc: no container yet"; all_ok=0; continue; fi
      status="$(docker inspect --format '{{.State.Status}}' "$cid" 2>/dev/null)"
      health="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$cid" 2>/dev/null)"
      _ft_log "  $svc: status=$status health=$health"
      [[ "$status" == "running" ]] || all_ok=0
      [[ "$health" == "healthy" || "$health" == "none" ]] || all_ok=0
    done < <(_ft_expected_services)
    [[ "$all_ok" -eq 1 ]] && break
    if (( SECONDS >= deadline )); then
      _ft_log "FAIL: stack not running+healthy within ${timeout}s"
      "${STACK_COMPOSE[@]}" ps >>"$FT_SETUP_LOG" 2>&1 || true
      return 1
    fi
    sleep 2
  done
  _ft_log "services running + healthy"

  # 3: SUT answers
  while :; do
    if "${STACK_COMPOSE[@]}" exec -T "$FT_SUT_SERVICE" agentdrill version >>"$FT_SETUP_LOG" 2>&1; then
      _ft_log "SUT answers: agentdrill version OK"
      break
    fi
    if (( SECONDS >= deadline )); then
      _ft_log "FAIL: SUT did not answer within ${timeout}s"
      return 1
    fi
    sleep 2
  done

  # 4: the host oMLX LLM endpoint (only when the case requires the LLM)
  if [[ "${FT_WITH_LLM:-0}" == "1" ]]; then
    while :; do
      if _ft_llm_reachable; then
        _ft_log "oMLX LLM endpoint responds (host ${FT_LLM_HOST_URL})"
        break
      fi
      if (( SECONDS >= deadline )); then
        _ft_log "FAIL: oMLX endpoint ${FT_LLM_HOST_URL} did not respond within ${timeout}s"
        return 1
      fi
      sleep 2
    done
  fi

  _ft_log "stack READY"
  return 0
}

# --- case lifecycle ----------------------------------------------------------
ft_case_begin() {
  local id="$1"
  ft_run_init
  FT_CASE_DIR="$FT_RUN_DIR/cases/$id"
  FT_LLM_DIR="$FT_CASE_DIR/artifacts/llm"
  mkdir -p "$FT_CASE_DIR/artifacts" "$FT_LLM_DIR"
  : > "$FT_CASE_DIR/commands.log"
  : > "$FT_CASE_DIR/stdout.log"
  : > "$FT_CASE_DIR/stderr.log"
  : > "$FT_CASE_DIR/assertions.ndjson"
  FT_CASE_STATUS="fail"
  FT_ASSERT_FAILED=0
  FT_ASSERT_GROUNDED=0
  FT_LLM_CAPTURED=0
  FT_CASE_DECLARED=0
  FT_DECLARE_LIMITATION=""
  FT_DECLARE_GATE=""
  echo "== case $id =="
}

# Resolve to `declared` for a P/F|D case whose environment is genuinely
# unavailable. Requires a named limitation + the plan/gate item that permits "or
# declared". A `declared` outcome for a hard gate is invalid and fails the case.
ft_declare() {
  local limitation="$1" gate="${2:-}"
  if [[ "$FT_CASE_CLASS" != "P/F|D" ]]; then
    echo "  DECLARE-INVALID $limitation (case class is $FT_CASE_CLASS, not P/F|D)" >&2
    FT_ASSERT_FAILED=1
    return 1
  fi
  FT_CASE_DECLARED=1
  FT_DECLARE_LIMITATION="$limitation"
  FT_DECLARE_GATE="$gate"
  printf '{"name":"declared","ok":true,"limitation":"%s","release_gate_item":"%s"}\n' \
    "$limitation" "$gate" >> "$FT_CASE_DIR/assertions.ndjson"
  echo "  DECLARED $limitation"
}

ft_record() {
  [[ -n "${FT_CASE_DIR:-}" ]] || return 0
  printf '+ %s\n' "$*" >> "$FT_CASE_DIR/commands.log"
}

# Run a command, tee stdout/stderr, and return its exit code.
ft_run() {
  ft_record "$@"
  local rc=0
  "$@" >> "$FT_CASE_DIR/stdout.log" 2>> "$FT_CASE_DIR/stderr.log" || rc=$?
  return "$rc"
}

# Execute a shell command inside a service container.
ft_exec() {
  local service="$1"; shift
  ft_record "compose exec $service $*"
  local rc=0
  "${STACK_COMPOSE[@]}" exec -T "$service" "$@" \
    >> "$FT_CASE_DIR/stdout.log" 2>> "$FT_CASE_DIR/stderr.log" || rc=$?
  return "$rc"
}

_ft_json_escape() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  printf '%s' "$s"
}

# Weak-assertion catalogue — the same shapes gen_cases.py rejects. An assertion
# that proves only *plumbing* (import / existence / json.tool / cannot-fail /
# bare-driver-with-unconditional-ok) is NOT a grounded check and cannot, on its
# own, justify a PASS. Deep verification: every PASS must rest on ≥1 grounded
# assertion (see ft_finalize).
_ft_weak_reasons() {
  local cmd="$1" reasons=""
  grep -qE "python3 +-c +['\"]import " <<<"$cmd" && reasons="$reasons import-only"
  grep -qF "|| true" <<<"$cmd" && reasons="$reasons cannot-fail"
  grep -qF "json.tool" <<<"$cmd" && reasons="$reasons json.tool"
  if grep -qE "\btest +-[fsn]\b" <<<"$cmd" && [[ "$cmd" != *grep* && "$cmd" != *"&&"* ]]; then
    reasons="$reasons existence-only"
  fi
  if grep -qE "python3 +/ft/scripts/[^ ]+\.py" <<<"$cmd" && [[ "$cmd" != *grep* && "$cmd" != *"&&"* ]]; then
    reasons="$reasons driver-only"
  fi
  printf '%s' "$reasons"
}

# ft_assert runs a command whose exit code IS the check. It records the *command*
# and a grounding verdict so a reviewer can see what was actually proved and so a
# weak assertion can never be mistaken for a grounded one.
ft_assert() {
  local name="$1"; shift
  local cmd="$*"
  local weak; weak="$(_ft_weak_reasons "$cmd")"
  local grounded="true"; [[ -n "$weak" ]] && grounded="false"
  if "$@" >> "$FT_CASE_DIR/stdout.log" 2>> "$FT_CASE_DIR/stderr.log"; then
    if [[ "$grounded" == "true" ]]; then FT_ASSERT_GROUNDED=$((FT_ASSERT_GROUNDED + 1)); fi
    printf '{"name":"%s","ok":true,"grounded":%s,"cmd":"%s"}\n' \
      "$name" "$grounded" "$(_ft_json_escape "$cmd")" >> "$FT_CASE_DIR/assertions.ndjson"
    echo "  PASS $name${weak:+ (WEAK:${weak# })}"
    return 0
  fi
  FT_ASSERT_FAILED=1
  printf '{"name":"%s","ok":false,"grounded":%s,"cmd":"%s"}\n' \
    "$name" "$grounded" "$(_ft_json_escape "$cmd")" >> "$FT_CASE_DIR/assertions.ndjson"
  echo "  FAIL $name" >&2
  return 1
}

# Record a failed assertion without running a command (for infrastructure
# failures: container up, daemon socket, empty store, 0 frames delivered).
ft_fail() {
  local name="$1"
  FT_ASSERT_FAILED=1
  printf '{"name":"%s","ok":false}\n' "$name" >> "$FT_CASE_DIR/assertions.ndjson"
  echo "  FAIL $name" >&2
}

# Record a passed assertion without running a command.
ft_pass() {
  local name="$1"
  printf '{"name":"%s","ok":true}\n' "$name" >> "$FT_CASE_DIR/assertions.ndjson"
  echo "  PASS $name"
}

ft_capture() {
  local src="$1" dest="$2"
  mkdir -p "$FT_CASE_DIR/artifacts/$dest"
  cp -R "$src"/. "$FT_CASE_DIR/artifacts/$dest/" 2>/dev/null || true
}

# Assert a shell command *inside the SUT container*.
ft_assert_sut() {
  local name="$1"; shift
  ft_assert "$name" ft_sut bash -lc "$*"
}

ft_case_end() {
  local id="$1" status="${2:-$FT_CASE_STATUS}"
  FT_CASE_STATUS="$status"
  # Leak gate: results are committed to git, so a case must never persist an
  # artifact carrying an unmasked secret. A leak fails the case.
  if grep -rqiIE 'sk-[A-Za-z0-9]{16,}|Bearer +[A-Za-z0-9._-]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}' \
        "$FT_CASE_DIR/artifacts" 2>/dev/null; then
    FT_ASSERT_FAILED=1
    printf '{"name":"no-secret-leak","ok":false,"grounded":true,"cmd":"scan artifacts for secrets"}\n' \
      >> "$FT_CASE_DIR/assertions.ndjson"
    echo "  FAIL no-secret-leak (unmasked secret in case artifacts)" >&2
    FT_CASE_STATUS="fail"
  else
    printf '{"name":"no-secret-leak","ok":true,"grounded":true,"cmd":"scan artifacts for secrets"}\n' \
      >> "$FT_CASE_DIR/assertions.ndjson"
    echo "  PASS no-secret-leak"
  fi
  {
    printf '{\n'
    printf '  "id": "%s",\n' "$id"
    printf '  "status": "%s",\n' "$status"
    printf '  "class": "%s",\n' "$FT_CASE_CLASS"
    printf '  "declared": %s,\n' "$([[ "$FT_CASE_DECLARED" -eq 1 ]] && echo true || echo false)"
    printf '  "grounded": %s,\n' "$([[ "${FT_ASSERT_GROUNDED:-0}" -ge 1 ]] && echo true || echo false)"
    printf '  "assertions_total": %s,\n' "${FT_ASSERT_TOTAL:-0}"
    printf '  "assertions_grounded": %s,\n' "${FT_ASSERT_GROUNDED:-0}"
    printf '  "llm_captured": %s,\n' "$([[ "${FT_LLM_CAPTURED:-0}" -eq 1 ]] && echo true || echo false)"
    if [[ "$FT_CASE_DECLARED" -eq 1 ]]; then
      printf '  "limitation": "%s",\n' "$FT_DECLARE_LIMITATION"
      printf '  "release_gate_item": "%s",\n' "$FT_DECLARE_GATE"
    fi
    printf '  "run_id": "%s",\n' "$FT_RUN_ID"
    printf '  "assertions": ['
    if [[ -s "$FT_CASE_DIR/assertions.ndjson" ]]; then
      paste -sd, "$FT_CASE_DIR/assertions.ndjson"
    fi
    printf ']\n}\n'
  } > "$FT_CASE_DIR/verdict.json"
  echo "== case $id: $status =="
}

ft_finalize() {
  # No skip: pass only if every assertion held. Any failure => fail.
  # DEEP VERIFICATION (must): a PASS must additionally rest on at least one
  # *grounded* assertion (a real check — not an import/existence/cannot-fail
  # shape), and an LLM-requiring case must have captured its request/response
  # pairs. A declared P/F|D case (environment genuinely unavailable) is
  # `declared`, a distinct terminal state, not a pass.
  local total=0
  if [[ -s "$FT_CASE_DIR/assertions.ndjson" ]]; then
    total=$(wc -l < "$FT_CASE_DIR/assertions.ndjson" | tr -d ' ')
  fi
  FT_ASSERT_TOTAL="$total"
  if [[ "$FT_ASSERT_FAILED" -ne 0 ]]; then
    FT_CASE_STATUS="fail"
  elif [[ "$FT_CASE_DECLARED" -eq 1 ]]; then
    FT_CASE_STATUS="declared"
  elif [[ "$total" -eq 0 ]]; then
    FT_CASE_STATUS="fail"
    echo "  FAIL no-assertions (a pass must be backed by >=1 assertion)" >&2
  elif [[ "${FT_STRICT_GROUNDING:-1}" == "1" && "$FT_ASSERT_GROUNDED" -eq 0 ]]; then
    FT_CASE_STATUS="fail"
    echo "  FAIL ungrounded (no grounded assertion; every assertion is plumbing)" >&2
  elif [[ "${FT_CASE_LLM:-0}" == "1" && "$FT_LLM_CAPTURED" != "1" ]]; then
    FT_CASE_STATUS="fail"
    echo "  FAIL no-llm-capture (LLM case with no captured request/response pair)" >&2
  else
    FT_CASE_STATUS="pass"
  fi
}

# Case-exit trap. In a shared-stack run the stack stays up across cases and is
# reset in place between them (see ft_reset_state and run-case.sh); the top-level
# runner tears it down once, at the end. A standalone case honors STACK_KEEP.
ft_teardown_on_exit() {
  local code=$?
  if [[ "${FT_SHARED_STACK:-0}" == "1" ]]; then
    exit "$code"
  fi
  if [[ "${STACK_KEEP:-}" == "1" ]]; then
    echo "==> STACK_KEEP=1 set; leaving the stack running"
    exit "$code"
  fi
  stack_teardown
  exit "$code"
}

# --- SUT lifecycle -----------------------------------------------------------
# The system-under-test home inside the container: the agentdrill output dir and
# all run artifacts live here (mounted on a named volume).
FT_SUT_HOME=/data/agentdrill

# Every case boots the FULL stack (all services) and verifies it is up. The stack
# is built once per run and kept up across cases; a non-recycle case is reset in
# place (ft_reset_state) instead of being destroyed. A `recycle` case mutates
# durable/container state that a soft reset cannot clear and is given a genuinely
# fresh stack (run-case.sh tears it down before it runs).
ft_up_sut() {
  if _ft_stack_up && ft_wait_ready; then
    ft_reset_state
    ft_pass "stack-reused"
  else
    _ft_boot_fresh
  fi
}

# --- build once + stack liveness ---------------------------------------------
# Build the images ONCE per run. Top-level runners call ft_build_images and export
# FT_IMAGES_BUILT=1, so every case's `up -d` skips `--build` (images do not change
# during a run). Without it (e.g. a standalone case) the first `up` builds.
ft_build_images() {
  if [[ "${FT_IMAGES_BUILT:-0}" == "1" ]]; then
    return 0
  fi
  mkdir -p "$FT_RUN_DIR"
  ft_record "compose build (once per run)"
  local rc=0
  "${STACK_COMPOSE[@]}" build "${FT_SERVICES[@]}" \
    >> "$FT_RUN_DIR/.build.log" 2>&1 || rc=$?
  # Also build the sandbox/agent-runner image (used by run_in_container and
  # tests/test_security_docker_llm.py). Same repo Dockerfile, harness tag.
  local runner="${AGENTDRILL_DOCKER_IMAGE:-agentdrill-agent-runner}"
  if ! docker image inspect "$runner" >/dev/null 2>&1; then
    ft_record "docker build $runner (repo Dockerfile)"
    docker build -t "$runner" -f "$REPO_ROOT/Dockerfile" "$REPO_ROOT" \
      >> "$FT_RUN_DIR/.build.log" 2>&1 || rc=$?
  fi
  export FT_IMAGES_BUILT=1
  return "$rc"
}

# Expected running services for the active run.
_ft_expected_services() {
  printf '%s\n' "${FT_SERVICES[@]}"
}

# True when every expected service has a running container.
_ft_stack_up() {
  local svc cid
  while IFS= read -r svc; do
    cid="$("${STACK_COMPOSE[@]}" ps -q "$svc" 2>/dev/null)"
    [[ -n "$cid" ]] || return 1
    [[ "$(docker inspect --format '{{.State.Running}}' "$cid" 2>/dev/null)" == "true" ]] || return 1
  done < <(_ft_expected_services)
  return 0
}

# Bring up the full stack and verify it (used only when the stack is not already
# running). Build happens once per run, so this is `up -d` on the shared path.
_ft_boot_fresh() {
  ft_up_all
  ft_verify_all
}

# --- per-case state reset (replaces `down -v`) -------------------------------
# Wipe the SUT home (run artifacts, caches, cloned agents) so each case starts
# clean WITHOUT destroying containers or volumes.
ft_reset_state() {
  ft_record "reset: restart SUT; wipe $FT_SUT_HOME"
  if "${STACK_COMPOSE[@]}" restart "$FT_SUT_SERVICE" \
      >> "$FT_CASE_DIR/stdout.log" 2>> "$FT_CASE_DIR/stderr.log"; then
    ft_pass "reset-sut-restart"
  else
    ft_fail "reset-sut-restart"
    return 1
  fi
  ft_sut bash -lc "shopt -s dotglob; rm -rf ${FT_SUT_HOME}/* 2>/dev/null; mkdir -p ${FT_SUT_HOME}; true" \
    >/dev/null 2>>"$FT_CASE_DIR/stderr.log" || true
  ft_pass "state-reset"
}

# Boot the FULL stack and verify every container is up. Called by EVERY case so
# the whole stack is up before any assertions run.
ft_up_all() {
  local args=(-d)
  [[ "${FT_IMAGES_BUILT:-0}" == "1" ]] || args+=(--build)
  ft_record "compose up ${args[*]} (full stack)"
  if "${STACK_COMPOSE[@]}" up "${args[@]}" "${FT_SERVICES[@]}" \
      >> "$FT_CASE_DIR/stdout.log" 2>> "$FT_CASE_DIR/stderr.log"; then
    ft_pass "stack-up"
  else
    ft_fail "stack-up"
  fi
  # Confirm the stack is genuinely ONLINE (running + healthy + SUT answers
  # [+ LLM]); the transcript is preserved in $FT_SETUP_LOG.
  if ft_wait_ready; then
    ft_pass "stack-ready"
  else
    ft_fail "stack-ready"
  fi
}

# Verify every service is running and every endpoint responds; records one
# assertion per service. Returns non-zero if any fail.
ft_verify_all() {
  local rc=0
  printf '%-16s %-10s %s\n' "SERVICE" "STATUS" "CHECK"
  local svc
  for svc in "${FT_SERVICES[@]}"; do
    local cid
    cid="$("${STACK_COMPOSE[@]}" ps -q "$svc" 2>/dev/null)"
    if [[ -z "$cid" ]]; then
      printf '%-16s %-10s %s\n' "$svc" "DOWN" "container missing"
      ft_fail "svc-$svc"; rc=1; continue
    fi
    printf '%-16s %-10s %s\n' "$svc" "$(docker inspect --format '{{.State.Status}}' "$cid" 2>/dev/null)" "container up"
    ft_pass "svc-$svc"
  done
  _check "agentdrill-version" "docker exec $("${STACK_COMPOSE[@]}" ps -q "$FT_SUT_SERVICE") agentdrill version"
  return "$rc"
}

_check() {
  local name="$1"; shift
  if bash -lc "$*" >/dev/null 2>&1; then
    printf '%-16s %-10s %s\n' "$name" "OK" "responds"
    ft_pass "ep-$name"
  else
    printf '%-16s %-10s %s\n' "$name" "FAIL" "no response"
    ft_fail "ep-$name"
    return 1
  fi
}

# Run argv inside the SUT container.
ft_sut() { ft_exec "$FT_SUT_SERVICE" "$@"; }

# Run the agentdrill CLI inside the SUT container.
ft_agentdrill() { ft_sut agentdrill "$@"; }

# Assert an agentdrill CLI invocation inside the SUT.
ft_assert_agentdrill() {
  local name="$1"; shift
  ft_assert "$name" ft_sut agentdrill "$@"
}

# --- LLM backend — the host oMLX server (OpenAI-compatible) ------------------
# There is no LLM container: the pinned LLM is **oMLX on the host**. A case that
# requires the LLM verifies the endpoint is reachable; if it is not, the case
# fails loudly (no fake green).

# True when the oMLX endpoint answers (host-local, or the container-facing URL).
_ft_llm_reachable() {
  curl -sf --max-time 5 "${FT_LLM_HOST_URL%/}/v1/models" >/dev/null 2>&1 \
    || curl -sf --max-time 5 "${FT_LLM_BASE_URL%/}/v1/models" >/dev/null 2>&1
}

# Require the LLM endpoint (used by LLM-requiring cases).
ft_llm_up() {
  export FT_WITH_LLM=1
  ft_record "require oMLX endpoint ${FT_LLM_HOST_URL}"
  if _ft_llm_reachable; then
    ft_pass "llm-endpoint-reachable"
  else
    ft_fail "llm-endpoint-reachable"
  fi
}

# Verify the LLM endpoint responds (alias used by some steps).
ft_llm_verify() { ft_llm_up; }

# Copy the SUT home (run artifacts, packs, caches) into the case artifacts.
ft_capture_sut() {
  local dest="$FT_CASE_DIR/artifacts/sut"
  mkdir -p "$dest"
  local cid
  cid="$("${STACK_COMPOSE[@]}" ps -q "$FT_SUT_SERVICE" 2>/dev/null)"
  if [[ -n "$cid" ]]; then
    docker cp "$cid":"$FT_SUT_HOME"/. "$dest/" 2>/dev/null || true
    docker logs "$cid" > "$dest/container.log" 2>&1 || true
  fi
}

# Copy the SUT home and assert it actually holds a run (an empty output dir is a
# failure, never a silent pass).
ft_capture_store() {
  ft_capture_sut
  if [[ -n "$(ls -A "$FT_CASE_DIR/artifacts/sut" 2>/dev/null)" ]]; then
    ft_pass "sut-has-artifacts"
  else
    ft_fail "sut-has-artifacts"
  fi
}

# Copy the SUT home WITHOUT asserting artifacts — for cases that do not produce a
# run (CLI validation, host-native probes).
ft_capture_sut_soft() { ft_capture_sut; }

# Capture container logs for a service into artifacts/logs/<service>.log.
ft_capture_logs() {
  local service="$1"
  mkdir -p "$FT_CASE_DIR/artifacts/logs"
  "${STACK_COMPOSE[@]}" logs --no-color "$service" \
    > "$FT_CASE_DIR/artifacts/logs/$service.log" 2>&1 || true
}

# --- LLM request/response capture (must) -------------------------------------
# Every LLM case records the full request/response pair(s) it made. Pairs land in
# $FT_LLM_DIR (artifacts/llm/) as <name>-request.json / <name>-response.json,
# sanitized (secrets masked). A case that needs the LLM but captured nothing is a
# failure (see ft_finalize), never a silent pass — the capture IS the evidence.

# Copy LLM pairs from a source directory (or a container path) into $FT_LLM_DIR.
ft_capture_llm() {
  local src="$1"
  mkdir -p "$FT_LLM_DIR"
  if [[ "${src}" == container:* ]]; then
    local cid
    cid="$("${STACK_COMPOSE[@]}" ps -q "$FT_SUT_SERVICE" 2>/dev/null)"
    if [[ -n "$cid" ]]; then
      docker cp "$cid:${src#container:}"/. "$FT_LLM_DIR/" 2>/dev/null || true
    fi
  else
    cp -R "$src"/. "$FT_LLM_DIR/" 2>/dev/null || true
  fi
}

# Assert the case captured at least one LLM request/response pair, that the pair
# is a **real** 2xx response (not an error stub), and that it is sanitized.
ft_assert_llm_capture() {
  local name="${1:-llm-capture}"
  local req resp real
  req=$(find "$FT_LLM_DIR" -name '*-request.json' 2>/dev/null | wc -l | tr -d ' ')
  resp=$(find "$FT_LLM_DIR" -name '*-response.json' 2>/dev/null | wc -l | tr -d ' ')
  real="$("$FT_PY" - "$FT_LLM_DIR" <<'PY'
import glob, json, sys
for f in glob.glob(sys.argv[1] + "/*-response.json"):
    try:
        d = json.load(open(f, encoding="utf-8"))
    except (OSError, ValueError):
        continue
    sc, body = d.get("status_code", 0), d.get("body", "")
    if isinstance(sc, int) and 200 <= sc < 300 and isinstance(body, str) and body.strip():
        print("ok"); break
PY
)"
  if [[ "$req" -ge 1 && "$resp" -ge 1 && "$real" == "ok" ]]; then
    # Deep verification: the capture must be sanitized (no raw bearer keys/tokens).
    if grep -rqiE 'sk-[A-Za-z0-9]{16,}|Bearer +[A-Za-z0-9._-]{20,}' "$FT_LLM_DIR" 2>/dev/null; then
      FT_ASSERT_FAILED=1
      printf '{"name":"%s","ok":false,"grounded":true,"cmd":"sanitize-scan %s"}\n' \
        "$name-sanitized" "$FT_LLM_DIR" >> "$FT_CASE_DIR/assertions.ndjson"
      echo "  FAIL $name-sanitized (unmasked secret in LLM capture)" >&2
      return 1
    fi
    FT_LLM_CAPTURED=1
    FT_ASSERT_GROUNDED=$((FT_ASSERT_GROUNDED + 1))
    printf '{"name":"%s","ok":true,"grounded":true,"cmd":"capture: %s request(s) + %s response(s); 2xx; sanitized"}\n' \
      "$name" "$req" "$resp" >> "$FT_CASE_DIR/assertions.ndjson"
    echo "  PASS $name ($req request(s), $resp response(s), 2xx, sanitized)"
    return 0
  fi
  FT_ASSERT_FAILED=1
  printf '{"name":"%s","ok":false,"grounded":true,"cmd":"capture: %s request(s) + %s response(s); real-2xx=%s"}\n' \
    "$name" "$req" "$resp" "${real:-no}" >> "$FT_CASE_DIR/assertions.ndjson"
  echo "  FAIL $name (no real 2xx LLM request/response pair captured)" >&2
  return 1
}

# Make a real LLM call through the pinned oMLX endpoint and record the pair, then
# assert the capture. Args: NAME [--prompt "..."] [--model M]
ft_llm_probe() {
  local name="${1:-llm}"
  local rc=0
  "$FT_PY" "$REPO_ROOT/scripts/fieldtest/llm_capture.py" --out "$FT_LLM_DIR" --name "$name" \
    --base-url "${FT_LLM_HOST_URL%/}/v1" --model "$FT_LLM_MODEL" "${@:2}" \
    >> "$FT_CASE_DIR/stdout.log" 2>> "$FT_CASE_DIR/stderr.log" || rc=$?
  if [[ "$rc" -eq 0 ]]; then ft_pass "llm-probe-ran"; else ft_fail "llm-probe-ran"; fi
  ft_assert_llm_capture "$name-captured"
}

# Retry a command until it succeeds or the timeout expires.
#   ft_wait_until NAME TIMEOUT cmd...
ft_wait_until() {
  local name="$1" timeout="$2"; shift 2
  local deadline=$((SECONDS + timeout))
  while ! "$@" >> "$FT_CASE_DIR/stdout.log" 2>> "$FT_CASE_DIR/stderr.log"; do
    if (( SECONDS >= deadline )); then
      echo "  TIMEOUT waiting for $name" >&2
      return 1
    fi
    sleep 1
  done
  return 0
}
