# maigret-mcp

Dockerized **Streamable HTTP MCP server** wrapping [Maigret](https://github.com/soxoj/maigret) for username OSINT searches.

## Features

- Run Maigret in a containerized environment
- Expose MCP over Streamable HTTP at `/mcp`
- Search one or multiple usernames
- Generate TXT / HTML / PDF / CSV / JSON reports
- Return report file paths and parsed TXT summary
- Restrict output to an internal `reports/` directory
- Avoid storing secrets in the repository

## Security notes

This project does **not** include API keys, tokens, cookies, proxy credentials, or other secrets.

By default, potentially sensitive or high-risk Maigret options are disabled in the MCP wrapper:

- `--ai`
- `--cloudflare-bypass`
- `--tor-proxy`
- `--i2p-proxy`
- arbitrary output paths

Use this tool only for public information discovery and follow applicable laws and platform terms.

## Quick start

```bash
docker run --rm \
  -p 8000:8000 \
  -v "${PWD}/reports:/app/reports" \
  m0eak/maigret-mcp:latest
```

MCP endpoint:

```text
http://localhost:8000/mcp
```

## Docker Compose

```bash
docker compose up -d
```

For local development build:

```bash
docker compose --profile build up --build
```

## MCP client config example

Use URL-based Streamable HTTP configuration:

```json
{
  "mcpServers": {
    "maigret-mcp": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

## Runtime environment

| Variable | Default | Description |
| --- | --- | --- |
| `MCP_HOST` | `0.0.0.0` | Bind address inside the container |
| `MCP_PORT` | `8000` | Streamable HTTP port |
| `MCP_PATH` | `/mcp` | MCP endpoint path |
| `MCP_STATELESS_HTTP` | `true` | Run Streamable HTTP in stateless mode |
| `MCP_JSON_RESPONSE` | `true` | Prefer JSON responses instead of SSE event streams |
| `MAIGRET_MCP_REPORTS_DIR` | `/app/reports` | Report output directory |

## Tools

### `search_username`

Search a single username.

### `search_usernames`

Search multiple usernames in one Maigret run.

### `maigret_stats`

Return Maigret database statistics.

### `list_reports`

List generated report files.

## Development

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
python -m maigret_mcp.server
```
