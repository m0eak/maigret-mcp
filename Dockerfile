FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000 \
    MCP_PATH=/mcp \
    MCP_STATELESS_HTTP=true \
    MCP_JSON_RESPONSE=true

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src
COPY vendor ./vendor

RUN pip install --upgrade pip \
    && pip install . \
    && python -c "import shutil; from pathlib import Path; import maigret; src=Path('/app/vendor/maigret/resources'); dst=Path(maigret.__file__).resolve().parent/'resources'; [shutil.copy2(src/name, dst/name) for name in ('data.json', 'db_meta.json') if (src/name).exists()]"

RUN mkdir -p /app/reports

VOLUME ["/app/reports"]

EXPOSE 8000

ENTRYPOINT ["python", "-m", "maigret_mcp.server"]
