# Reporting & Statistics — Reference

**Status:** normative (M10). Reporter: `src/agentdrill/reporting/`. Design:
[../design/reporting.md](../design/reporting.md). Success metrics: [PRD 07](../prd/07-success-metrics.md).

## Formats

`render(report, fmt)` / `publish(report, fmt)` render one run to:

| Format | `fmt` | Use |
|---|---|---|
| JSON | `json` | machine consumption |
| Markdown | `markdown` | PR comments |
| GitHub-Actions | `github` | workflow annotations (`::warning`) |
| HTML | `html` | self-contained, offline (inline styles, no scripts, no network) |
| PDF | `pdf` | compliance consumers (minimal valid PDF) |

An unknown format raises `ValueError`.

## Honesty rules (enforced)

- **Misses mandatory (R5).** `publish` runs `check_honesty` first: the outcome split must equal the
  report rows, so a run cannot publish with a miss or degradation hidden (`HonestyError`). Unknown
  outcomes are rejected.
- **Multi-seed (F29).** Every published number is `mean ± std` over **≥3 distinct pinned seeds**
  (`seed_stats`); `require_multi_seed` raises `SingleRunError` otherwise. `build_release` applies this
  to every pack.
- **Confidence intervals (F55).** A published rate is a `RateCI` carrying a seeded bootstrap CI
  (`bootstrap_ci`), formatted `blocked 87% [81%, 92%] (n, seeds)`. `require_ci` rejects a bare
  percentage (`BarePercentageError`).
- **No composite "security score".** The outcome split + misses, never an average that hides one
  (ADR-0013).

## Severity rubric (F41)

`rate_finding(case_id, attack_class=, exposure=)` scores `attack-class × exposure` to
`critical`/`high`/`medium`/`low` with a rationale (PRD 12 R25). Attack classes: `injection`,
`exfiltration`, `destructive`, `privilege_escalation`. Exposure: `external`, `partner`, `internal`,
`privileged`. `sort_findings` orders most-severe first, then pack, then case id.

## Coverage heat-map (F53)

`build_heatmap(report)` produces a pack/tag × control matrix; each cell is `blocked` / `partial` /
`missed` / `untested`. `HeatMap.delta(other)` reports per-cell status changes against a previous
release.

## Traces per row (F56)

Each row carries a trace reference; `TraceStore.resolve(row)` returns the full
`Trace` (trajectory + evidence) in one hop, keyed by `trace_ref` (falling back to the case id). A
missing trace fails loudly (`TraceNotFoundError`).

## Trend store (F23)

`TrendStore.record(release, rates)` accumulates per-defense-class rates; `deltas(klass)` gives the
per-release series and `what_got_worse()` answers, in one call, which classes dropped between the two
latest releases.

## Benchmark schema + submission (F57, R4)

A `BenchmarkRelease` is a table per pack (`PackBenchmark`: `pack_ref`, `seeds`, `rates` (a `RateCI`
per outcome), `misses`, `manifest`). `export_benchmark(release, dest)` writes a pinned
`benchmark.json` bundle for fork → run → PR submission. `reproduces(expected, actual)` verifies a
third party's numbers (rates within tolerance) and miss sets match.
