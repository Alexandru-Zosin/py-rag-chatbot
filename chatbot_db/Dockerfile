FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# System deps: curl for downloads; ca-certs for TLS; tini for PID 1
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates tini && \
    rm -rf /var/lib/apt/lists/*

# Install uv and ensure it is on PATH via a stable symlink
RUN set -eux; \
    curl -LsSf https://astral.sh/uv/install.sh | sh; \
    if [ -x /root/.local/bin/uv ]; then ln -sf /root/.local/bin/uv /usr/local/bin/uv; \
    elif [ -x /root/.cargo/bin/uv ]; then ln -sf /root/.cargo/bin/uv /usr/local/bin/uv; \
    else echo "uv not found after install" >&2; exit 1; fi

WORKDIR /app

# Install Python deps first (best layer caching)
COPY requirements.txt /app/requirements.txt
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -r /app/requirements.txt

# Copy sources and scripts
COPY src /app/src
COPY scripts /app/scripts
RUN chmod +x /app/scripts/*.sh || true

EXPOSE 8000
VOLUME ["/chroma", "/app/data"]

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["bash", "/app/scripts/entrypoint.sh"]
