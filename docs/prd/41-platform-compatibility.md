# PRD 41 — Platform Compatibility & Support Matrix

**BLUF:** "Harness-agnostic" is a promise, not a measure. Replace binary "compatible" with a graded scale **L0 listed → L1 config-aware → L2 driven → L3 observed (witnessed) → L4 gated (contract pack in CI)**, a transparent **prioritization model**, a **reference-harness policy** (headline tables use open-source harnesses so third parties can reproduce), a **version-follow SLA**, and one published number — **adoption-weighted coverage**. Scope every platform in priority order: coding agents, frameworks/SDKs, protocols (MCP/A2A), enterprise/cloud, defenses the drills target, host/CI/model runtimes.

**Status:** Draft — v0.1.0 addition (2026-10-10) · **Owner:** @deghosal-2026 · **Parent:** agentsec-ecosystem #209 · **Features:** F103 · **Reqs:** R77

## Why

- Today a harness is "compatible only when its pack passes in CI" — binary, no depth; one "Cursor ✓" can mean config-lint or full drive.
- Harnesses release weekly (Claude Code, Codex CLI, Cursor, Copilot, Gemini CLI/Antigravity, OpenCode, Cline, …); a level claim rots silently without an SLA.
- Reproduction (CUJ-3, the success bar) requires the reproducer to *have* the harness → prefer open harnesses for headline tables.

## Requirements (v0.1.0)

| # | Requirement | Acceptance criterion |
|---|---|---|
| **R77** | A **compatibility matrix** with levels L0–L4, per-surface rows, a published prioritization model, a reference-harness policy, a version-follow SLA, and an **adoption-weighted coverage (AWC)** metric. | ≥ 2 Tier-1 harnesses at L2+ (PRD), recommend ≥ 3 incl. one open; AWC ≥ 0.60 at v0.1.0; matrix rows never older than the SLA. |

## Features

| # | Feature | Req | Notes |
|---|---|---|---|
| **F103** | **Platform compatibility & support matrix**: L0–L4 levels with evidence requirements · prioritization model (`0.30·Adoption + 0.25·AttackSurface + 0.20·Driveability + 0.15·Reproducibility + 0.10·Strategic`) · reference-harness policy (≥2 open-source at L3+) · version-follow SLA (matrix ≤ 7 d; L4 ≤ 72 h; nightly driver canary) · AWC metric · per-platform attack-surface models (rules/instruction files, MCP config/trust, hooks/plugins/skills, auto-approve, web-fetch, repo-content injection, sandbox profile, cloud/background agents, subagent delegation) | R77 | Scope list: coding agents · frameworks/SDKs (LangGraph, OpenAI Agents SDK, Claude Agent SDK, CrewAI, Google ADK, MS Agent Framework, PydanticAI, smolagents) · protocols (MCP dated revisions, A2A 1.0, AGENTS.md/Skills, AP2) · enterprise/cloud (Bedrock AgentCore, MS Foundry/Copilot Studio, Vertex/ADK, Agentforce, ServiceNow) · defenses under test · host/CI/model runtimes |

### Reference-harness policy
At least two **open-source** harnesses always at L3+ (OpenCode, Codex CLI, Gemini/Antigravity CLI, Cline, Aider, Goose). Proprietary-harness results appear in a **separate table**, never alone in a compatibility claim. Results state "harness defaults" vs. "auto-approve."

### Host/CI/model runtimes
- Hosts: macOS arm64 + Linux x86_64/arm64 P0; Windows via WSL2 P1.
- CI: GitHub Actions + GitLab CI P0; Jenkins/CircleCI/Buildkite/Azure P1; K8s/Argo/Tekton fleet.
- Model roles **separate** (driver ≠ judge ≠ attacker), local-first (MLX/Ollama/LM Studio/vLLM/llama.cpp) with a **judge-free deterministic subset**.

## CUJs

### CUJ-60 — Per-harness depth
A platform security lead asks, per harness, which of the 25 enterprise-relevant attacks were *driven and witnessed* vs. inferred. **Success:** level table per harness with versions.

### CUJ-61 — Add my harness
An embedder adds a harness: L1 in ≤1 day, L2 in ≤1 week via the driver SDK; the conformance kit reports the level reached. **Success:** SLA met.

## Success metrics

| Metric | Target |
|---|---|
| Harnesses at L2+ at v0.1.0 | ≥ 2 Tier-1 (recommend ≥ 3 incl. one open) |
| Harnesses at L3+ within 2 releases | ≥ 4 |
| Adoption-weighted coverage (AWC) | ≥ 0.60 at v0.1.0 → ≥ 0.80 within 2 releases |
| New-harness time-to-L2 (community adapter) | ≤ 5 working days |
| Harness release → matrix update | ≤ 7 days (L4 ≤ 72 h) |
| L3+ matrix rows older than N-2 versions | 0 |
| Driver-breakage caught by nightly canary before a user | ≥ 90% |
| Cross-OS deterministic outcome parity (macOS arm64 vs Linux x86_64) | ≥ 99.5% |
| Judge-free subset share of enforcement cases | ≥ 70% |
| Attack content leaving the machine without explicit consent | **0** |

## Target inventory (detail)

**As of 2026-10.** Rankings/versions change monthly — re-verify. Sources: 2026 agent/framework roundups, vendor docs, one Mar-2026 comparison. Items are **P0/P1/P2** priority with recommended L-level at v0.1.0.

### Coding agents & agentic IDEs
| Pri | Harness | Why | License / reproducibility | Surfaces to model | Rec. level |
|---|---|---|---|---|---|
| P0 | **Claude Code** | Top Terminal-Bench entry; deep hooks/permissions/MCP; enterprise adoption | Proprietary CLI | `CLAUDE.md`, settings/permissions, hooks, MCP config, subagents, auto-accept, namespace sandbox + network block, SDK/headless | L3 |
| P0 | **Codex CLI** (OpenAI) | Strong TB result; cheapest/task; Apache-2.0; kernel sandbox default | Open (Apache-2.0) | `AGENTS.md`, approval modes, sandbox profiles, MCP, cloud tasks | L3 (open reference) |
| P0 | **OpenCode** (anomalyco) | Largest OSS agent (~200k★, MIT); provider-agnostic; MCP+LSP+subagents; plugins/skills; **this team's harness** | Open (MIT) | `opencode.json(c)`, plugins, skills, MCP, permissions, server/ACP, local models | L3 (open reference) |
| P0 | **Cursor** | Dominant agentic IDE; cloud/background agents; OS sandbox (early 2026) | Proprietary IDE | `.cursor/rules`, MCP, auto-run/yolo, background agents, sandbox, hooks | L2 |
| P0 | **GitHub Copilot** (agent mode, coding agent, CLI) | Largest install base; coding agent runs in Actions → CI-runner abuse | Proprietary | `.github/copilot-instructions.md`, `.github/agents/`, MCP, Actions runners, PR-triggered injection | L2 (coding-agent path → L3 via Actions) |
| P1 | **Gemini CLI / Antigravity CLI** | Free tier moved to Antigravity CLI (2026-06); Apache-2.0 CLI | Open CLI | `GEMINI.md`, MCP, sandbox flags, built-in web fetch | L2 |
| P1 | **Cline** | Largest OSS VS Code agent (~66k★ Apache-2.0); Plan/Act step approval | Open | approval flow, MCP marketplace, `.clinerules` | L2 |
| P1 | **Windsurf (Devin Desktop)** | Large IDE base; *reported* approval-prompt-only (verify) → negative control | Proprietary | rules, MCP, memories | L1→L2 |
| P1 | **Aider** | Mature OSS CLI; git-native; polyglot leader | Open | git hooks, `.aider*`, shell commands | L2 |
| P2 | **Kiro (AWS), Kilo Code, Roo Code, Goose (Block), Amp, Zed, JetBrains Junie, Mistral Vibe, Qwen Code, Continue** | Long tail; some large in segments | mixed | per-harness | L0–L1 (community SDK) |

**Per-harness attack surface** (modeled in drivers): writable instruction/rules files (ASI01/06; ATLAS *Modify AI Agent Configuration*); auto-approve/yolo (ASI02/05); approval-dialog fidelity ("lies-in-the-loop", ASI09); MCP config/server trust (poisoning/rug-pull/shadowing); hooks/plugins/skills (content-swap); built-in web fetch (indirect injection); repo-content injection; secrets in env/dotfiles; sandbox profile (escape-to-host); cloud/background agents (blast radius, tenant isolation); subagent delegation (privilege inheritance).

### Frameworks & SDKs
| Pri | Framework | Why | Integration mode (fidelity) | Framework-specific surface |
|---|---|---|---|---|
| P0 | **LangGraph / LangChain** (1.2) | Most deployed for stateful production | OTel `gen_ai.*` + adapter | checkpoint tampering, state injection between nodes, HITL interrupt bypass, tool-node arg smuggling |
| P0 | **OpenAI Agents SDK** (native sandbox, sub-agents, MCP) | Largest vendor SDK | adapter + tracing | handoff injection, guardrail ordering, sandbox escape, session store |
| P0 | **Claude Agent SDK** | Deepest MCP; powers Claude Code | SDK driver | permission callbacks, hooks, subagents |
| P1 | **CrewAI** (~52k★; MCP + A2A) | Largest multi-agent community | adapter | role/backstory injection, delegation chain abuse, shared crew memory |
| P1 | **Google ADK 2** | Native A2A + Agent Cards, MCP | adapter | Agent Card spoofing, cross-agent trust |
| P1 | **Microsoft Agent Framework 1.0** | Enterprise/.NET reach | adapter | group-chat manager injection |
| P1 | **PydanticAI, smolagents** | Typed tools / code-agents | adapter | code-execution agents (ASI05) |
| P2 | LlamaIndex, Mastra, Vercel AI SDK, Strands (AWS), Semantic Kernel, Haystack | breadth | community | — |

**Integration modes (ranked fidelity):** (1) protocol-level (MCP/A2A/HTTP); (2) OTel-observed (`invoke_agent`/`execute_tool`/`plan`/`create_memory` … — semconv *Development*); (3) framework adapter (drives framework primitives). Every framework starts at mode 1+2 (L2); mode 3 only if adoption justifies.

### Protocols, specs & gateways
- **MCP** — drill across ≥3 dated revisions; roles: client/host, server, gateway, registry; transports stdio/Streamable HTTP/(legacy SSE). **Auth (OAuth 2.1):** RFC 8707 resource indicators & audience validation, RFC 9728 metadata, Client ID Metadata Documents, DCR deprecation — cases: token passthrough/confused deputy, audience-mismatch replay, redirect confusion, consent bypass. **Taxonomy coverage:** map to MCPSecBench (17), MCP-SafetyBench (20), MCPTox P1–P3. **Attack classes:** poisoning (param/command/filesystem/redirect/network/dependency), function overlap, preference manipulation, shadowing, return-value injection, rug-pull, DNS rebinding/localhost, session hijack, SSRF via tool, prompt/resource/sampling abuse. **Stealth** ⇒ mandatory witness.
- **A2A 1.0** — signed Agent Cards, task delegation: card forgery/replay, capability over-claim, delegation chain privilege inheritance, cross-org smuggling, unsigned-card downgrade (ungate: A2A is stable).
- **Instruction/skill formats** — `AGENTS.md`, Agent Skills (`SKILL.md`), `CLAUDE.md`, rules: instruction injection via repo content, content-swap at same version, resource traversal, precedence confusion.
- **Payments** — AP2: mandate forgery/replay, over-authorized spend (spec-gated, P2).
- **Gateways/proxies** — MCP/AI/API gateways are **defense targets** (see defense taxonomy below).
- **Telemetry** — OTel GenAI + MCP conventions (`mcp.method.name`, `mcp.session.id`); pin semconv version.

### Enterprise & cloud platforms
| Pri | Platform | Drill mode | Notes |
|---|---|---|---|
| P1 | **AWS Bedrock AgentCore** | remote target via MCP/A2A + CloudTrail witness | Bedrock Guardrails = defense target |
| P1 | **Microsoft Foundry / Copilot Studio / M365 Copilot** | remote target; **purple tenant** | EchoLeak-class history; vendor tool unsupported surfaces (function tools, browser, computer-use, connected agents) |
| P1 | **Google Vertex AI Agent Engine / ADK** | remote target | native A2A + Agent Cards |
| P2 | **Salesforce Agentforce, ServiceNow AI Agents, Workday/SAP agents** | remote target, sandbox orgs only | tenant-safe cases only |
| P2 | **Zapier / n8n / Make-class** | HTTP target | citizen-development overlap |
| P2 | Databricks Agent Bricks, Snowflake Cortex Agents, Cloudflare Agents/AI Gateway | remote target | edge/data-plane |

**Tenant-safety (non-negotiable):** (1) customer-owned tenants/sandbox orgs only, ownership verified pre-fire ([PRD 35](35-rules-of-engagement-and-safe-fire.md)); (2) purple-environment pattern, **canary data only** ([PRD 26](26-independent-effect-witness.md)); (3) transient runs where offered; (4) rate/cost ceilings (metered); (5) `tos_reviewed` recorded per platform.

### Defenses under test (the things we drill)
| Class | Examples | Decision point | Evidence |
|---|---|---|---|
| Prompt/content classifiers | Llama Guard / Prompt Guard, Lakera Guard, Azure Prompt Shields, Bedrock Guardrails, NeMo Guardrails, Guardrails AI, Prisma AIRS, Vigil | input/output allow/deny/transform | verdict + latency |
| Policy engines | OPA/Rego, Cedar, policyweave output | tool-call authorize | decision log |
| Gateways/proxies | agentgate, vendor MCP/AI gateways | tool-call/egress route | gateway log + **witness** |
| Credential brokers | agentkeys, vault issuers, Auth0 step-up/CIBA | grant/deny/revoke | token events + canary use |
| OS/process sandboxes | Codex kernel sandbox, Claude Code namespace, Cursor OS sandbox, gVisor, Firecracker, Docker/devcontainers, Seatbelt/Landlock | syscall/FS/network confinement | denial events + **witness** |
| MCP/skill scanners | mcp-scan-class, Snyk/Invariant, Cisco/Zenity/Noma-class | scan verdict pre-install | verdict vs. detonation truth ([PRD 36](36-extension-detonation-lab.md)) |
| HITL controls | approval dialogs, CIBA push, step-up MFA | consent decision fidelity | decision vs. executed action |
| Halt/revoke | agenthalt, cloud IAM revoke, token revoke | cessation | kill-time probe |

**Priority:** P0 own Wave-0 stack + OPA/Cedar + Llama Guard/Prompt Guard + NeMo + each coding-agent built-in sandbox. P1 Bedrock Guardrails, Azure Prompt Shields, Lakera Guard, Docker/gVisor/Firecracker, one MCP gateway + one scanner. P2 Prisma AIRS, Guardrails AI, Vigil, CIBA/step-up, vendor AI gateways. **OSS/free first** (reproducibility).

## Dependencies
F3, F14, F36, F45, F46, F49, F72 · [PRD 25](25-attacker-strength-and-pressure.md), [PRD 26](26-independent-effect-witness.md), [PRD 29](29-bring-your-own-defense.md), [PRD 36](36-extension-detonation-lab.md), [PRD 42](42-standards-and-claims.md).

## Boundaries & non-goals
- Not a harness quality ranking; we describe what we could drive and what happened, never rank harnesses.
- A harness's own built-in defenses are part of the target, not noise; results label defaults vs. auto-approve.

## Open questions
1. Per-surface rows (CLI vs. IDE) as separate matrix rows (recommend: yes).
2. Weight disputes → public issue with 14-day SLA (like F32).
