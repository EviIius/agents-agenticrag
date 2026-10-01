FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN groupadd --system agenticrag && useradd --system --gid agenticrag --home-dir /app agenticrag

COPY pyproject.toml README.md ./
COPY src ./src

RUN python -m pip install --no-cache-dir ".[documents,web]" \
    && mkdir -p /app/.data \
    && chown -R agenticrag:agenticrag /app

USER agenticrag
VOLUME ["/app/.data"]
EXPOSE 8787

HEALTHCHECK --interval=20s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8787/healthz', timeout=2).read()"

CMD ["python", "-m", "agenticrag", "serve", "--host", "0.0.0.0", "--port", "8787", "--allow-remote", "--no-open"]
