# Ollaborate Desk 0.2

A local task assistant inspired by Energy, Claude Cowork, and ChatGPT Work: state an outcome, gather context, delegate to specialists, and review the result. The implementation uses Ollaborate for local agents and a built-in offline file index. When LibreIndex is installed, semantic vector retrieval replaces the built-in lexical search. No account, CDN, remote model, or cloud connector is required.

## Start

On the computer that runs the assistant, install Ollama, Python 3.10+, and the project dependencies while online. Pull models before disconnecting:

```bash
ollama pull qwen3:8b
pip install .
OLL_DESK_FILES="$HOME/Documents" ollaborate-desk
```

Open `http://127.0.0.1:8765`. Click **Re-index files** before running a task. On Windows PowerShell, set `$env:OLL_DESK_FILES = "$HOME\Documents"` and then run `ollaborate-desk`. Pre-download Python wheels if installation itself must occur offline.

For semantic retrieval, install LibreIndex separately, pull `embeddinggemma`, and set `OLL_DESK_EMBEDDING` if desired. `OLL_DESK_MODEL` selects an already downloaded Ollama model. `OLL_DESK_DATA` sets the location for the local databases and reviewed outputs. Ollama must be on a local loopback address (`OLLAMA_HOST`, default `http://127.0.0.1:11434`). The web UI shows NVIDIA GPU name and VRAM use when `nvidia-smi` is available. Ollama itself handles GPU placement; Desk does not call CUDA or NVIDIA cloud services directly.

## Implemented

- Outcome task UI, local task history, and draft review.
- Built-in SQLite full-text search over PDF, Markdown, text, CSV, and JSON. If LibreIndex is installed separately, semantic vector retrieval and its confidence warning are used instead.
- Ollaborate planning and drafting specialists through Ollama.
- User-triggered indexing and user-triggered Markdown save; existing filenames are preserved.
- Loopback-only web service and local SQLite task store.

## Odysseus integration (optional)

Odysseus can launch Desk's read-only MCP companion as a local stdio server. Install the extra on the same machine as Odysseus, with packages downloaded ahead of time for an offline installation:

```bash
pip install '.[odysseus]'
```

In Odysseus **MCP servers**, add a stdio server named `Ollaborate Desk` with command set to the absolute path of the installed `ollaborate-desk-mcp` executable and empty arguments (`[]`). Set its environment to the same `OLL_DESK_DATA`, `OLL_DESK_FILES`, `OLL_DESK_MODEL`, and `OLLAMA_HOST` values as Desk, where applicable. For a containerized Odysseus installation, install Desk inside the container and mount the selected documents and Desk data into it; paths and executable must refer to the container filesystem. Index the documents in Desk first. You can verify the connection in Odysseus's MCP server list.

The companion offers `search_files`, `list_drafts`, and `get_draft`. It cannot create tasks, save files, or execute commands. Odysseus may have its own model and network settings; configure its models and other tools for local use if the combined workflow must remain offline. No Odysseus source code is included here; the programs communicate over the MCP protocol. This bridge is opt-in and does not change Desk's default pipeline.

## Product direction

| Inspiration | Local interpretation | State |
| --- | --- | --- |
| Energy | Outcome prompt and a visible result | Initial task flow implemented |
| Claude Cowork | Work in a selected folder; inspect resulting artifacts | File context and draft save implemented |
| ChatGPT Work | Specialists, evidence, review, reusable work | Specialist pipeline implemented; skills and workflows planned |
| NVIDIA GPU | Fast local model inference and visible VRAM | Ollama acceleration and GPU status available |
| Strands Harness | Sessions, tool gates, and scoped action runtime | [Evaluation result](evaluation/RESULTS_2026-09-25.md): retain Ollaborate default |
| Odysseus | Local workspace consuming Desk's indexed evidence and drafts | Optional read-only MCP bridge implemented |

The next milestone is a local action runtime: explicit folder grants, proposed file edits with diffs, approvals, rollback, and an audit log. After that, add reusable skill files, task schedules, and optional connectors limited to local or intranet applications. A fully offline machine cannot browse public websites, send internet email, or act in cloud applications. Connected work can be offered as a separately enabled mode, but must never be represented as offline.

## Limits

The assistant cannot yet manipulate apps or files other than a reviewed Markdown save. When LibreIndex is installed, its retrieval confidence is a similarity score, not the probability that a claim is correct. Source markers generated in drafts need checking against the displayed excerpts. Scanned PDFs require OCR. The application assumes a trusted single-user computer. If the indexed folder has no readable content, indexing fails clearly; the existing index may persist until a new successful index is built.

LibreIndex is not yet available to a clean installation from the configured package index. The optional `semantic` extra becomes usable once LibreIndex has a published distribution. Until then, install its source wheel separately before starting Desk.
