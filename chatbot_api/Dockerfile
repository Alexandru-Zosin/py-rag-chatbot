# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
RUN pip install --no-cache-dir uv
WORKDIR /app

# Only requirements first for better layer caching
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# --- Dev stage (used by docker-compose for hot-reload mounts)
FROM base AS dev
COPY . /app
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

# --- Optional minimal runtime image (use if you do not need bind mounts)
FROM base AS runtime
COPY . /app
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
