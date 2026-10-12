#!/usr/bin/env python3
"""agentdrill WBS issue generator/pusher (v0.1.0 additions, M23–M32).

Composes the SAME issue body depth as the existing v0.1.0 issues (Why / Behavior-What /
How / Data & schema impact / Security & privacy / Edge cases / Testing / Risks &
mitigations / Acceptance criteria / Dependencies / References / Definition of done),
with the marker `<!-- wbs:<item_id> -->`.

Usage:
  python3 scripts/wbs_issues.py update    # edit existing issues (by WBS Issue column)
  python3 scripts/wbs_issues.py create    # create any work item missing an issue
  python3 scripts/wbs_issues.py push      # create missing, then update all
"""
import re, sys, subprocess, tempfile, pathlib

REPO = "agentic-suite/agentdrill"
ROOT = pathlib.Path(__file__).resolve().parents[1]
WBS = ROOT / "docs/wbs/v0.1.0"
PARTS = [f"wbs-v0.1.0-part{n}-{s}.md" for n, s in [
    (13, "effect-witness-bypass"), (14, "byod-integrations"),
    (15, "context-governance"), (16, "frontier-platform-standards"),
    (17, "fieldtest-release")]]
NEW_MS = ["M23","M24","M25","M26","M27","M28","M29","M30","M31","M32"]

M = {
"M23": dict(name="Independent effect witness & adversary lab",
 why="the oracle currently grades a defense largely from the defense's own evidence — circular — so a defense can log `denied` while a side effect still lands, and stealth attacks are invisible. Independent witnesses outside the defended stack and a reusable hostile-environment kit make enforcement proof non-circular.",
 what="cases declare forbidden/preserved effects; witnesses (canary FS, network sinkhole, honey credentials, process/syscall, side-effect ledger, human surface) confirm effects; a two-oracle verdict emits `witness_discrepancy`/`blocked_silently`/`witness_unavailable`; a seed-deterministic, loopback-only Adversary Lab provides hostile counterparties and sinks.",
 how="Implement effect declarations in the pack schema; build the witnesses in a separate trust domain with a hash-chained log; compare defense decision × witness into the verdict set; build the loopback lab (evil MCP server, test IdP/OAuth, registries, rogue API, A2A peer, sinks) with a ground-truth event log and `lab@version` pin.",
 schema="Cases gain `effects.forbidden[]`/`effects.preserved[]`; `.agentdrill/witness/` (records + hash chain) and `.agentdrill/lab/` (pinned definitions); `run-manifest.json` gains `witness` (version, coverage, live) and `lab@version`.",
 edge="witness failed/untrusted ⇒ `witness_unavailable` (never publish `blocked`); witness disagrees with defense ⇒ `witness_discrepancy`; lab never reaches a real network; a case with no declared effect is rejected.",
 deps="M3 (runner), M6 (oracle engine), M8 (fixtures/manifest). New subsystem — no predecessor port.",
 design="design/effect-witness-and-lab.md", prds="[PRD 26](https://github.com/agentic-suite/agentdrill/blob/main/docs/prd/26-independent-effect-witness.md) · [PRD 27](https://github.com/agentic-suite/agentdrill/blob/main/docs/prd/27-adversary-lab.md)"),
"M24": dict(name="Attacker strength, pressure & bypass search",
 why="a `blocked` result must state the attacker's strength and effort, and rules written against the *forms* of an action must be searched for equivalent *routes* to the same effect.",
 what="attacker-capability tiers T0–T3 with `Hold@k`/`ASR@k` + CIs and pressure curves; a bounded, seeded effect-based bypass search with delta-debug minimization, family dedup, a per-effect coverage report, and auto-promotion of confirmed bypasses to regressions.",
 how="Label every result with tier + k; compute all-of-k/any-of-k with bootstrap CIs and first-break percentiles; build the route-family catalogue and a seeded bounded search judged by the M23 witness; minimize with delta-debugging, dedup into families, and promote to regression cases.",
 schema="`run-manifest.json` gains `attacker.{tier,k,mutation_path,seed}`; results gain `hold_at_k`,`asr_at_k`,`pressure_curve`; `.agentdrill/bypass/<family>.json` holds confirmed bypasses + minimal reproducers.",
 edge="deterministic controls: `Hold@k` measures route coverage, not stochastic variance; T3 stays deferred/local-only; no payload leakage; budgets cap the search.",
 deps="M23 (witness). T3 deferred (DD-44).",
 design="design/attacker-strength-and-bypass.md", prds="[PRD 25](https://github.com/agentic-suite/agentdrill/blob/main/docs/prd/25-attacker-strength-and-pressure.md) · [PRD 28](https://github.com/agentic-suite/agentdrill/blob/main/docs/prd/28-policy-bypass-search.md)"),
"M25": dict(name="Bring-your-own-defense & neutral head-to-head",
 why="drilling only the ecosystem's own stack reads as a vendor benchmark; neutral, independent proof is scarce and valuable.",
 what="a Defense Contract + SDK + conformance kit; an OSS-first Defense Zoo; a neutral head-to-head under published rules with no composite score or ranking.",
 how="Define the contract (decision points, I/O, evidence, config digest, fail-mode, version, ToS notes); build the conformance kit; ship reference adapters; build the identical-input head-to-head comparison; encode the neutrality rules (pre-registration, right-of-reply, licensed-config-only, conflict disclosure).",
 schema="A `Defense` contract object + `config_digest`; conformance-level records; head-to-head report artifacts bound to config digests.",
 edge="no composite score ever; measures a defense in a configuration, never the product; ToS-restricted benchmarking → OSS/consent-only.",
 deps="M23 (witness), M24 (metrics), M26 (standards export).",
 design="design/byod-and-neutral-head-to-head.md", prds="[PRD 29](https://github.com/agentic-suite/agentdrill/blob/main/docs/prd/29-bring-your-own-defense.md)"),
"M26": dict(name="Security ecosystem integrations",
 why="findings must land where buyers already work; the PRD names no interchange standards today.",
 what="emit SARIF/JUnit/OTel/OCSF/OSCAL/STIX; import Inspect/promptfoo/garak/AgentDojo/PyRIT; BAS-style SIEM/EDR detection validation; reliability (idempotency, DLQ, offline spool).",
 how="Implement and schema-validate each emitter; implement importers; implement the SIEM detection-validation query; make upserts idempotent with stable fingerprints, retries/DLQ, signed webhooks and an offline spool.",
 schema="Findings gain interoperable projections (SARIF results, OCSF events, OSCAL assessment-results, STIX bundles); stable `partialFingerprints`.",
 edge="payloads/PII excluded by default; content capture opt-in; no mandatory hosted service.",
 deps="M27 (ledger), M10 (benchmark), M19 (oracle versions).",
 design="design/integrations.md", prds="[PRD 38](https://github.com/agentic-suite/agentdrill/blob/main/docs/prd/38-security-ecosystem-integrations.md) · [PRD 42](https://github.com/agentic-suite/agentdrill/blob/main/docs/prd/42-standards-and-claims.md)"),
"M27": dict(name="Backtest, attack-path & incident intake",
 why="drilling should follow reachable risk and real history, and fresh advisories should become packs fast.",
 what="trace backtest + shadow mode with a false-block budget; an attack-path/blast-radius graph with path status; an incident-to-pack compiler (cite-or-drop, efficacy check, dual-use screen).",
 how="Replay redacted agentwatch sessions against a candidate policy; run a log-only shadow beside the enforced defense; build the capability graph from inventory and derive reachable-harm paths with AIVSS severity; compile advisories into draft packs from lab generators under a dual-use screen.",
 schema="New entities/artifacts: `AttackPath`, backtest/shadow reports, incident briefs; trace-derived cases tagged `origin: production-trace`.",
 edge="replay is a model of reality (fidelity disclosed); shadow must be side-effect-free; reachability ≠ exploitability; intake content is untrusted → runs in the lab.",
 deps="M23 (witness), M8 (fixtures/manifest), M13 (efficacy).",
 design="design/backtest-path-intake.md", prds="[PRD 30](https://github.com/agentic-suite/agentdrill/blob/main/docs/prd/30-trace-backtest-and-shadow.md) · [PRD 31](https://github.com/agentic-suite/agentdrill/blob/main/docs/prd/31-attack-path-and-blast-radius.md) · [PRD 32](https://github.com/agentic-suite/agentdrill/blob/main/docs/prd/32-incident-to-pack-compiler.md)"),
"M28": dict(name="Exposure ledger, attestations & rules of engagement",
 why="the CI gate must be livable (waivers that never relabel a miss), the proof consumable (signed attestations with freshness), and the tool safe to run anywhere (rules of engagement).",
 what="exposure ledger + time-boxed waivers; in-toto/Sigstore drill attestations with freshness/invalidation; rules of engagement + fail-closed preflight + safe-fire interlocks.",
 how="Implement the finding lifecycle and signed waivers (expiry, drilled compensating control, auto-reopen, known-miss budget); implement the in-toto `agentdrill/drill-result/v1` predicate + Sigstore + invalidation + consumers; implement the RoE file, preflight, interlocks and scope receipts.",
 schema="New entities: `FindingStatus`, `Waiver`, `DrillAttestation`; `.agentdrill/waivers/` and `.agentdrill/attestations/`.",
 edge="waivers never relabel; integrity findings not waivable; expired waivers never suppress; zero out-of-scope actions; destructive effects canary-only.",
 deps="M23, M24, M9 (severity), M19 (oracle versions).",
 design="design/exposure-attestation-roe.md", prds="[PRD 33](https://github.com/agentic-suite/agentdrill/blob/main/docs/prd/33-exposure-ledger-and-waivers.md) · [PRD 34](https://github.com/agentic-suite/agentdrill/blob/main/docs/prd/34-drill-attestations-and-deploy-gate.md) · [PRD 35](https://github.com/agentic-suite/agentdrill/blob/main/docs/prd/35-rules-of-engagement-and-safe-fire.md)"),
"M29": dict(name="Detonation, Break-It & frontier attack classes",
 why="extensions are a documented attack surface that static scanners miss; crowds find novel bypasses; several OWASP ASI categories lack efficacy-verified packs.",
 what="dynamic extension detonation (Behavior Report + prior-version drift); the Break-It program (witness auto-verify, coordinated disclosure, regression conversion); the frontier attack classes (identity/OAuth, approval abuse, memory, wallet, cascade, browser, multimodal; AP2 stub).",
 how="Run unknown extensions in the hermetic lab under a driver agent and observe behavior via M23 witnesses; stand up the Break-It range with witness auto-verification and coordinated disclosure; ship each frontier class as a pack with twins, witnesses and cleanup.",
 schema="New entities: `BehaviorReport`; new pack classes with ASI/ATLAS tags; bypass-family catalogue growth.",
 edge="extension detonation is bounded evidence (never 'safe'); strict isolation, no real egress; documented patterns only; dual-use review per class.",
 deps="M23, M24, M27, M28.",
 design="design/detonation-breakit-frontier.md", prds="[PRD 36](https://github.com/agentic-suite/agentdrill/blob/main/docs/prd/36-extension-detonation-lab.md) · [PRD 37](https://github.com/agentic-suite/agentdrill/blob/main/docs/prd/37-break-it-program.md) · [PRD 39](https://github.com/agentic-suite/agentdrill/blob/main/docs/prd/39-frontier-attack-classes.md)"),
"M30": dict(name="Trace explorer, platform matrix & standards",
 why="investigation speed, a measurable notion of 'compatible', and defensible claims.",
 what="a local trace explorer (incl. the defense-vs-witness view); a graded platform compatibility matrix (L0–L4) + AWC; the standards claim vocabulary + linter + master table.",
 how="Build the local viewer (overview, case step-through, defense-vs-witness, pressure curve, bypass-family tree, diff/attribution, HITL queue, inert rendering, a11y); build the graded matrix + reference-harness policy + version-follow SLA + AWC; implement the claims linter, master standards table, version pins + drift watcher and evidence indexes.",
 schema="Viewer artifacts + a compatibility matrix artifact; standards tags/pins in results; evidence indexes per framework.",
 edge="no hosted viewer; no composite score; levels/metrics measured not asserted; untrusted content inert.",
 deps="M23, M24, M26, M27, M28.",
 design="design/trace-explorer-and-platform-standards.md", prds="[PRD 40](https://github.com/agentic-suite/agentdrill/blob/main/docs/prd/40-trace-explorer.md) · [PRD 41](https://github.com/agentic-suite/agentdrill/blob/main/docs/prd/41-platform-compatibility.md) · [PRD 42](https://github.com/agentic-suite/agentdrill/blob/main/docs/prd/42-standards-and-claims.md)"),
"M31": dict(name="Field tests",
 why="field tests prove the whole system end to end on a real deployed stack and state honestly what was **not** tested.",
 what="run every CUJ-1..CUJ-63 end to end (core + additions) under a signed RoE; publish FIELD_TEST_REPORT.md with a not-tested list; fix every defect with a regression test.",
 how="Drive the bundled demo stack + a real deployed stack; execute every CUJ; collect evidence; publish the report; fix defects with regressions; add a nightly field-test CI job.",
 schema="Field-test evidence + FIELD_TEST_REPORT.md; regression tests per defect.",
 edge="the report must state what was **not** tested; runs only under a signed RoE in an ephemeral/purple environment.",
 deps="M23–M30.",
 design="field-test/v0.1.0/field-test-plan.md", prds="[PRD 07](https://github.com/agentic-suite/agentdrill/blob/main/docs/prd/07-success-metrics.md) · [PRD 04](https://github.com/agentic-suite/agentdrill/blob/main/docs/prd/04-users-and-cujs.md)"),
"M32": dict(name="Release readiness",
 why="release readiness is its own gate: v0.1.0 is tagged here and the predecessor is retained privately, never deleted.",
 what="release tooling + SBOM + signed provenance; first-run ≤ 15 min; security audit + compliance/evidence indexes; version/backwards-compat policy; release notes + compatibility table (L0–L4, AWC); tag v0.1.0; make the predecessor private.",
 how="Run `make release-dry-run`; time a clean-machine quickstart; publish the security audit, compliance matrix + evidence indexes; enforce version consistency; publish release notes + the generated compatibility table; tag v0.1.0; set the predecessor repo private (never delete).",
 schema="Signed release artifacts (CycloneDX SBOM, checksums, provenance); release notes + compatibility table.",
 edge="nothing is tagged before this milestone; mock/fixture attestations are non-evidence; predecessor is retained, never deleted.",
 deps="M31 (and all prior).",
 design="release/v0.1.0/", prds="[PRD 07](https://github.com/agentic-suite/agentdrill/blob/main/docs/prd/07-success-metrics.md) · [PRD 09](https://github.com/agentic-suite/agentdrill/blob/main/docs/prd/09-roadmap.md) · [PRD 43](https://github.com/agentic-suite/agentdrill/blob/main/docs/prd/43-evidence-register-and-method.md)"),
}

def gh(args, input=None):
    return subprocess.run(["gh"] + args, input=input, text=True, capture_output=True)

def gh_ok(args, input=None):
    r = gh(args, input=input)
    if r.returncode != 0:
        raise SystemExit(f"gh {' '.join(args)} failed:\n{r.stderr[:400]}")
    return r.stdout

def clean(s):
    return re.sub(r"\s+", " ", s.replace("**", "").replace("`", "")).strip()

def parse():
    items = []
    for fn in PARTS:
        mnum = None
        for line in (WBS / fn).read_text().splitlines():
            mh = re.match(r"^## Milestone (M\d+) — ", line)
            if mh:
                mnum = mh.group(1); continue
            it = re.match(r"^\|\s*(\d+\.[A-Za-z0-9]+)\s*\|", line)
            if it and mnum in NEW_MS:
                cells = [c.replace("\\|", "|").strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
                if len(cells) < 6:
                    continue
                items.append(dict(fn=fn, mnum=mnum, id=cells[0], task=cells[1], desc=cells[2],
                                  deliverable=cells[3], acceptance=cells[4],
                                  issue=int(cells[5].lstrip("#")) if cells[5].lstrip("#").isdigit() else None))
    return items

def body(it):
    c = M[it["mnum"]]
    tid, task, desc = it["id"], it["task"], it["desc"]
    deliverable = it["deliverable"] or "the deliverable"
    acceptance = clean(it["acceptance"]) or clean(task)
    gate = tid[-2:] in (".T", ".C", ".L", ".CR", ".D") or tid.endswith((".T",".C",".L",".CR",".D"))
    if tid.endswith(".T"):
        this = f"this ticket owns **test authoring** for {it['mnum']} — it turns the milestone's behaviour into an executable gate."
        beh = f"This item delivers **tests**: {desc}."
    elif tid.endswith(".C"):
        this = "this ticket owns the **coverage gate** for the milestone."
        beh = "This item enforces code coverage ≥ 95% on the milestone's modules with no untested new path."
    elif tid.endswith(".L"):
        this = "this ticket owns the **lint/type gate** for the milestone."
        beh = "This item enforces `ruff` zero violations and `mypy --strict` clean across the milestone."
    elif tid.endswith(".CR"):
        this = "this ticket owns **code review** for the milestone."
        beh = "This item records review findings in `docs/wbs/v0.1.0/codereview-log.md` and resolves them before closure."
    elif tid.endswith(".D"):
        this = "this ticket owns the **design/reference docs** for the milestone."
        beh = "This item updates and links the milestone's design/reference docs; a link-check must pass."
    else:
        this = f"{task} — it produces the **{deliverable}** deliverable and unblocks later items."
        beh = f"This item delivers **{deliverable}**: {desc}"
    return f"""# {it['mnum']} {tid} — {clean(task)}

> `[0.1.0 {it['mnum']}]` — owning milestone: **{it['mnum']} {c['name']}**. Source item: `{it['fn']}` `{tid}`.

**Why.** {c['why'][0].upper()+c['why'][1:]} _This item:_ {this}

**Behavior / What.** {c['what'][0].upper()+c['what'][1:]} {beh}

**How.**
{c['how'][0].upper()+c['how'][1:]}

Steps:
1. Read the linked PRD/design sections above before writing code.
2. Implement "{clean(task)}": {clean(desc)}
3. Wire it into **{deliverable}** and expose it through the documented surface (CLI/SDK) within this milestone.
4. Handle failure modes **loudly** — invalid input, unknown references, and partial state must never pass silently (`docs/reference/errors.md`).
5. Keep it deterministic where the milestone requires (pins, seeds, fixtures) and evidence-bound where results are produced.
6. Update docs as you go (this milestone's `.D` item).

**Data & schema impact.** {c['schema']}

**Security & privacy.** Standard: never persist secrets; fail loudly; no enforcement added.

**Edge cases.** {c['edge']}

**Testing.**
- Test-first (RED → GREEN): write a failing test asserting _{acceptance}_, run it (**RED**), implement, run it (**GREEN**).
- Minimum cases: Unit + integration + fault-injection tests for the new paths.
- Happy path **and** at least one failure path; determinism where applicable; no regression in earlier items of this milestone.

**Risks & mitigations.** Scope creep beyond this item — keep the diff to the linked WBS item.

## Acceptance criteria
- [ ] {acceptance}
- [ ] Wired into **{deliverable}**; reachable from the documented surface
- [ ] Failure modes handled loudly (invalid input / unknown reference / partial state)
- [ ] All tests pass; every new code path has a test
- [ ] Code coverage ≥ 95% on touched modules
- [ ] `ruff` zero violations; `mypy --strict` clean
- [ ] Code review recorded in `docs/wbs/v0.1.0/codereview-log.md`; all findings resolved
- [ ] Design/reference docs updated and linked from the WBS

## Dependencies
{c['deps']}

## References
- WBS: `docs/wbs/v0.1.0/{it['fn']}` · index: `docs/wbs/v0.1.0/wbs-v0.1.0-index.md`
- {c['prds']} · [design/{c['design'].split('/')[-1]}](https://github.com/agentic-suite/agentdrill/blob/main/docs/{c['design']})

## Definition of done
Implemented + tests passing + committed + pushed + this issue closed (or commented with status), with a
checkpoint recorded in the WBS index. Commits are conventional and DCO-signed.

<!-- wbs:{tid} -->
"""

def edit(it):
    tf = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False); tf.write(body(it)); tf.close()
    gh_ok(["issue", "edit", str(it["issue"]), "--repo", REPO,
           "--title", f"[0.1.0 {it['mnum']}] {it['id']} {clean(it['task'])}"[:200],
           "--body-file", tf.name])
    pathlib.Path(tf.name).unlink()

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "update"
    items = parse()
    missing = [i for i in items if not i["issue"]]
    print(f"parsed {len(items)} items; missing issue numbers: {len(missing)}")
    if mode in ("create", "push"):
        labels = [("0.1.0","1d76db","agentdrill v0.1.0"),("wbs","5319e7","WBS work item")]
        for n,c,d in labels:
            gh(["label","create",n,"--repo",REPO,"--color",c,"--description",d,"--force"])
        for it in missing:
            tf = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False); tf.write(body(it)); tf.close()
            out = gh_ok(["issue","create","--repo",REPO,
                         "--title", f"[0.1.0 {it['mnum']}] {it['id']} {clean(it['task'])}"[:200],
                         "--body-file", tf.name, "--milestone", f"0.1.0 — {it['mnum']} {M[it['mnum']]['name']}",
                         "--label","0.1.0","--label","wbs"])
            it["issue"] = int(out.strip().splitlines()[-1].rstrip("/").split("/")[-1])
            pathlib.Path(tf.name).unlink()
            print(f"created #{it['issue']} {it['mnum']} {it['id']}")
    n = 0
    for it in items:
        if mode in ("update", "push") and it["issue"]:
            edit(it); n += 1
            if n % 20 == 0:
                print(f"  updated {n}...")
    print(f"updated {n} issues")

if __name__ == "__main__":
    main()
