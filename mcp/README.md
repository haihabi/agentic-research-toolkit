# mcp/

MCP servers. One self-contained directory per server: `mcp/<server-name>/`.

| Server | Purpose | Transport | Entrypoint |
|--------|---------|-----------|------------|
| [`overleaf/`](overleaf/) | Overleaf projects as file operations (list/read/edit/add/move/delete, binary assets, local PDF build) over the git bridge | stdio | `overleaf-mcp` (`overleaf_mcp.server:main`) |
