# maigret-mcp

Dockerized MCP server wrapping [Maigret](https://github.com/soxoj/maigret) for username OSINT searches.

## Features

- Run Maigret in a containerized environment
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
docker build -t maigret-mcp .
docker run --rm -i -v "%cd%/reports:/app/reports" maigret-mcp
```

## MCP client config example

```json
{
  "mcpServers": {
    "maigret-mcp": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-v",
        "C:/Users/m0eak/Documents/GitHub/maigret-mcp/reports:/app/reports",
        "maigret-mcp"
      ]
    }
  }
}
```

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
