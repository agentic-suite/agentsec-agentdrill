# Evidence & Expected Telemetry

**Status:** normative (M7). Design: [../design/evidence-integration.md](../design/evidence-integration.md).
Code: `src/agentdrill/evidence/`.

agentdrill **consumes** the agentwatch record + security-event schema (DD-05). One schema, one source of truth.

## Reading events (7.1)

`read_events(source)` accepts a list of event dicts, a `{"events": [...]}` envelope, or a JSON file path.

```python
class AgentWatchEvent(BaseModel):
    event: str            # denied | policy-fired | secret-detected | revoked | halted
    ref: str | None
    ts: str | None
    actor: str | None
    detail: str | None
    case_id: str | None   # the case the recorder tagged it to
```

An event name outside the vocabulary fails loudly with `ConfigError`.

## Binding evidence (7.2)

`bind_case(case_id, events)` collects the refs whose `case_id` matches. An empty binding is a **gap**:
`evidence_gap(binding)` returns a `Finding(type="evidence_gap")` — no result ends up without evidence or an
explicit gap.

## Expected telemetry (7.3, F52)

A case declares `oracle.expect_telemetry` — the events a **true block** must produce.
`validate_expected_telemetry(case, verdict, events)` returns a `telemetry_gap` finding when a `blocked`
verdict lacks the declared events (a `missed`/`degraded` case has no such requirement).

## Evidence in artifacts (7.4)

`attach_evidence(artifact, events)` writes the typed `Evidence` refs into `CaseArtifact.evidence`, persisted
in `artifacts/<case_id>.json` — a result reconstructs its evidence.

## Coverage reconciliation (7.5, F26)

`coverage_report(snapshot, exercised, explained=…)` reports exercised vs. unexercised surfaces from the
agentwatch inventory (`ReconSnapshot`); `unexplained` (`gap:unexplained`) counts unexercised surfaces with no
explanation — the goal is zero.

## Findings

| Finding | When |
|---|---|
| `evidence_gap` | a result has no bound evidence |
| `telemetry_gap` | a `blocked` verdict without its declared `expect_telemetry` events |
