# Strands Harness evaluation for Ollaborate Desk

Date: 2026-09-25
Decision: evaluate an optional runtime adapter; keep Ollaborate as Desk's default agent orchestration.

## Why revisit

Strands Harness (Apache-2.0) is now an open-source Python/TypeScript harness. It supplies sessions, memory, context management, tracing, skills, MCP, subagents, tool interventions, and evaluations. Its Python SDK supports locally hosted Ollama. Those are relevant to Desk's roadmap for durable tasks and controlled local actions. Sources: [repository](https://github.com/strands-agents/harness-sdk), [harness overview](https://strandsagents.com/docs/user-guide/harness/), [Ollama provider](https://strandsagents.com/docs/user-guide/sdk/model-providers/ollama/).

## Fit with the existing product

| Capability | Current Desk | Possible Strands contribution | Decision |
| --- | --- | --- | --- |
| Local models | Ollaborate agents through loopback Ollama | Ollama provider | Keep the local endpoint invariant; benchmark as optional runtime. |
| File knowledge | Built-in FTS5; optional LibreIndex | Tool or retrieval plugin | Preserve LibreIndex citations and confidence; do not swap retrieval implicitly. |
| Task history | SQLite draft history | Resumable sessions and context management | Evaluate session resume across process restart. |
| Actions | Reviewed Markdown save | Tool loop, interventions, shell/file tools | Prototype scoped actions only after OS and path policy are implemented. |
| Offline guarantee | Loopback model endpoint, no web tools | Configurable harness | Explicitly disable web/network tools and prove network denial outside prompts. |
| Differentiation | Small Ollama-first orchestration and local UX | General-purpose harness | Keep Ollaborate public API independent. Avoid making Strands a hard dependency. |

## Configuration requirements for a spike

- Install Strands only with a separate `strands` extra, never as the default runtime dependency.
- Supply an explicit `OllamaModel(host="http://127.0.0.1:11434", model_id=...)`; never rely on `create_harness()` model defaults, which use Bedrock.
- Begin with `builtin_tools=[]`, `builtin_plugins=[]`, `memory=False`, `skills=False`, and no MCP servers. Pass only an explicit read-only retrieval tool when needed. The default harness includes shell, file, web, programmatic tool calling, and subagent tools.
- Validate the endpoint as loopback and deny outbound traffic at an OS/container boundary in offline mode. A system prompt or intervention rule is not a network boundary.
- For local actions, grant an explicit directory; show proposed diffs; require review before write, delete, or command execution; record an audit event and support rollback. Consider Strands Shell with narrow `copy` binds. Its own security documentation calls it a mediation layer, not a hardened sandbox, and states its policy does not cover other agent tools.

Sources: [configuration reference](https://strandsagents.com/docs/user-guide/harness/reference/configuration/), [interventions](https://strandsagents.com/docs/user-guide/harness/configure/interventions/), [Shell security model](https://strandsagents.com/docs/user-guide/shell/security/).

## Decision gate

Implement a small adapter that exposes the same `run(task, evidence) -> draft` contract as Desk's current runtime. On the same local machine and downloaded model, compare 20 representative tasks: factual file questions, drafting, no-evidence queries, adversarial instructions inside documents, and multi-step local tasks. Record answer quality, grounded citation accuracy, latency, memory use, process-restart continuity, and attempted network/file boundary violations. Include tests proving that an unapproved write, a path escape, and an outbound request are blocked. Run with the network interface disabled as an end-to-end check.

Adopt a Strands-backed option only if it improves multi-step completion or durability without worse citation quality and passes every offline and approval test. Otherwise, borrow isolated design ideas (sessions, interventions, trace format) in Desk and Ollaborate. Do not replace Ollaborate's orchestration merely because the upstream harness is available.
