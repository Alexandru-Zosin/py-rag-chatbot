#!/usr/bin/env bash
set -euo pipefail

# Settings
: "${CHROMA_HOST:=0.0.0.0}"
: "${CHROMA_PORT:=8000}"
: "${CHROMA_PATH:=/chroma}"
: "${READY_TIMEOUT:=120}"   # seconds to wait for server

# Ensure DB dir exists and perms OK
mkdir -p "${CHROMA_PATH}"

# Start Chroma server in background
echo "[entrypoint] starting chroma server..."
chroma run \
  --path "${CHROMA_PATH}" \
  --host "${CHROMA_HOST}" \
  --port "${CHROMA_PORT}" \
  >/var/log/chroma.log 2>&1 &

# Wait for server to be ready
echo "[entrypoint] waiting for chroma to be ready at http://127.0.0.1:${CHROMA_PORT} ..."
for i in $(seq 1 "${READY_TIMEOUT}"); do
  if curl -fsS "http://127.0.0.1:${CHROMA_PORT}/api/v2/heartbeat" >/dev/null 2>&1 \
     || curl -fsS "http://127.0.0.1:${CHROMA_PORT}/heartbeat" >/dev/null 2>&1; then
    echo "[entrypoint] chroma is up."
    break
  fi
  sleep 1
  if [ "$i" -eq "${READY_TIMEOUT}" ]; then
    echo "[entrypoint] chroma did not become ready in time." >&2
    tail -n 200 /var/log/chroma.log || true
    exit 1
  fi
done

# Export PYTHONPATH so src imports work
export PYTHONPATH="/app/src:${PYTHONPATH:-}"

# Run ingestion (ingest_books.py decides whether to skip or not)
echo "[entrypoint] running conditional ingestion..."
if python -u /app/src/ingest_books.py; then
  echo "[entrypoint] ingestion step finished."
else
  echo "[entrypoint] ingestion script exited with non-zero status." >&2
  exit 1
fi

# Keep the server in foreground (PID 1) by tailing the log
echo "[entrypoint] chroma running. Tailing logs..."
exec tail -F /var/log/chroma.log
