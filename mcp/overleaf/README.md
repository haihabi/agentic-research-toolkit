# overleaf-mcp

MCP server that exposes an Overleaf project as plain file operations — list,
read, edit, add, move, delete, plus binary assets and a local PDF build. Git is
the sync transport under the hood (Overleaf's git bridge) and is never surfaced:
every mutating call auto-pulls, merges, commits, and pushes.

## Requirements

- **Python ≥ 3.10** and **git** on `PATH`.
- A **paid Overleaf plan** (or institutional licence) with git integration, and a
  **git token**: Overleaf → Account Settings → Git integration (personal token,
  works across all your projects), or a project's Menu → Git (per-project token).
- For `compile_project` only: a **TeX distribution with `latexmk`** (TeX Live,
  MacTeX, MiKTeX). Every other tool works without TeX.

## How auth works

The token is read **once, from `OVERLEAF_GIT_TOKEN` at process startup** — never a
tool argument, never echoed in a result. It is handed to git through a
`GIT_ASKPASS` helper fed by the environment, so it never lands in `argv` (visible
to `ps`) and never in `.git/config` on disk; the stored remote is just
`https://git@git.overleaf.com/<id>`. git output is token-redacted before it can
reach an error message.

## Setup

```bash
cd mcp/overleaf
uv venv
uv pip install -e .
cp .env.example .env   # then fill in OVERLEAF_GIT_TOKEN
```

## Configuration

| Env var | Required | Default |
|---|---|---|
| `OVERLEAF_GIT_TOKEN` | yes | — |
| `OVERLEAF_MCP_WORKSPACE` | no | platform data dir (e.g. `~/Library/Application Support/overleaf-mcp`) |
| `OVERLEAF_MCP_GIT_NAME` / `OVERLEAF_MCP_GIT_EMAIL` | no | `overleaf-mcp` / `overleaf-mcp@localhost` |
| `OVERLEAF_MCP_MAX_BINARY_MB` | no | `25` |
| `OVERLEAF_MCP_COMPILE_TIMEOUT` | no | `120` |

## Running

```bash
# Inspector UI (verify tools before wiring a client)
uv run mcp dev src/overleaf_mcp/server.py

# Direct stdio run (what a client launches; sits waiting for a connection)
OVERLEAF_GIT_TOKEN=... uv run overleaf-mcp
```

Client registration snippets live in `adapters/{claude-code,codex,gemini}/`.

## Tools

| Tool | Purpose |
|---|---|
| `add_project(overleaf_project_id, local_name)` | One-time: register + clone a project |
| `list_projects()` | List locally registered projects |
| `sync_project(local_name)` | Pull latest Overleaf changes into the local copy |
| `list_files(local_name, subdir="")` | List files (syncs first) |
| `read_file(local_name, file_path)` | Read a UTF-8 text file (syncs first) |
| `read_binary_file(local_name, file_path)` | Read a binary file as base64 (syncs first) |
| `edit_file(local_name, file_path, content, message=None)` | Overwrite a text file, then sync |
| `add_file(local_name, file_path, content, message=None)` | Create a text file, then sync |
| `add_binary_file(local_name, file_path, content_base64, message=None)` | Create/replace a binary file, then sync |
| `delete_file(local_name, file_path, message=None)` | Delete a file, then sync |
| `move_file(local_name, src_path, dst_path, message=None)` | Rename/move a file (one commit, history kept), then sync |
| `get_conflicts(local_name)` | Check for conflicts; on conflict, return base/mine/theirs per file |
| `resolve_conflict(local_name, resolutions, message=None)` | Apply resolved content for every conflicted file and sync |
| `compile_project(local_name, root_file=None, engine=None)` | Build to PDF locally with latexmk; returns success, pdf_path, errors, log tail |

`add_project` is the one unavoidably git-shaped step: Overleaf's bridge has no
"list my projects" endpoint, so you supply the project ID once (from the
project's Git settings), remembered locally thereafter.

## What "sync" does on every edit / add / move / delete

1. `git fetch` + `git merge` — pull anything changed on Overleaf (e.g. edits in
   the web editor) since the last sync.
2. Apply your change.
3. Commit and push.
4. If the push races with another change, re-sync once and retry.

Reads (`list_files`, `read_file`, `read_binary_file`) do a lighter **fetch +
fast-forward-only** update: they never merge and never fail on a conflict. If the
local copy has diverged, a read returns the local state and the next mutation
surfaces the conflict.

## Merge conflicts are surfaced, not auto-resolved

If step 1 hits a real conflict (same lines changed on both sides), the merge is
**aborted** and the call fails with the conflicted file list — your change is not
applied. Silently picking a side can leave conflict markers or broken syntax in a
`.tex` file that only shows up when the paper fails to compile.

To resolve:

1. `get_conflicts(local_name)` → for each conflicted file, `base` (common
   ancestor), `mine` (local), `theirs` (Overleaf). Nothing is changed.
2. Decide the final content for each file.
3. `resolve_conflict(local_name, resolutions={"path/to/file.tex": "…final…"})`
   with an entry for **every** file `get_conflicts` reported. Missing any → nothing
   is applied and the missing names are returned.

`get_conflicts` and `resolve_conflict` each independently attempt the merge and
abort on conflict, so the local clone is never left half-merged between calls.

## compile_project

Syncs, then runs `latexmk` in the clone with output to a git-excluded `.build/`
directory, so a compile never changes what gets pushed. `root_file` is
auto-detected (`main.tex` / `paper.tex`, else the `.tex` containing
`\documentclass`); `engine` from a `% !TEX program = …` line, else `pdflatex`.
Returns `{success, root_file, engine, pdf_path, duration_s, errors, log_tail}`.
The host's TeX toolchain can differ from Overleaf's, so a clean local build is a
strong signal, not a guarantee.

## Limitations

- Text tools assume UTF-8 (`.tex` / `.bib` / `.bbl`); use the binary tools for
  figures and PDFs. No Git LFS (the Overleaf bridge doesn't support it); mind
  Overleaf's per-file size limit.
- One token per server process. For multiple Overleaf accounts, run separate
  instances with different `OVERLEAF_GIT_TOKEN` / `OVERLEAF_MCP_WORKSPACE`.
- Every edit / add / move / delete is its own commit — history is granular.
- Windows: the `GIT_ASKPASS` helper is emitted as a `.cmd`; less exercised than
  the POSIX path.

## Tests

```bash
uv run pytest
```

A local bare repo stands in for `git.overleaf.com` — no network, no real token.
Compile tests auto-skip when `latexmk` is absent.
