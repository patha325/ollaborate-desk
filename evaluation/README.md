# Strands runtime evaluation

This evaluation exercises Ollaborate and Strands Harness with the same local file excerpts and the same two-stage plan-and-draft shape. It does not install Strands into Desk's default runtime.

## Reproduce the deterministic run

```bash
python -m venv .venv
.venv/bin/python -m pip install -e '.[dev,evaluation]'
.venv/bin/python evaluation/compare.py --output evaluation-result.json
.venv/bin/python -m pytest -q
```

On Windows PowerShell, use `.venv\Scripts\python.exe` in place of `.venv/bin/python`. The fixture replaces Ollama's client in-process; it tests provider calls, prompts, model selection, evidence plumbing, and tool exposure. It **does not** measure model quality, GPU performance, or a network security boundary. The fixture produces one fixed response per case. Do not interpret its latency numbers as a model benchmark.

## Run the live comparison on your NVIDIA PC

Install Ollama and pull `qwen3:8b` first. Then:

```bash
.venv/bin/python evaluation/compare.py --live --model qwen3:8b --output live-result.json
```

The script rejects non-loopback Ollama URLs. It runs four representative cases (supported fact, unsupported question, and two hostile excerpts). Review every output in the JSON. The automated `sourced_fact_and_citation` check is deliberately narrow; inspect the wording and cited excerpts yourself. The live comparison does not grant shell, write, web, or MCP tools. For a strict offline test, disconnect or block outbound network traffic at the OS boundary while the run executes. Check VRAM and model placement with `ollama ps` and `nvidia-smi` separately.

## Scope

Strands Harness is configured with an explicit Ollama model and zero tools, plugins, skills, memory, or background tasks for the fixture comparison. A separate session probe enables only a local session directory, reconstructs the agent, and verifies prior context is included in the next model request. The evaluation does not test long-running autonomous work, intervention handlers, Strands Shell, or an adversarial model with real tool access.
