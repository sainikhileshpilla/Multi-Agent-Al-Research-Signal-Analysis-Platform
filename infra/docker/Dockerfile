# ─────────────────────────────────────────────────────────────────────────────
# AI Signal Research Platform — Dockerfile
#
# Build:  docker build -f infra/docker/Dockerfile -t ai-signal-platform .
# Run:    docker run -p 8000:8000 ai-signal-platform
# ─────────────────────────────────────────────────────────────────────────────

# Python 3.12 slim keeps the image small (~130 MB base).
FROM python:3.12-slim

# ── System packages ───────────────────────────────────────────────────────────
# curl  → used by the Docker healthcheck (GET /health)
# build-essential + libgomp → needed by onnxruntime (ChromaDB's local embeddings)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# ── uv ────────────────────────────────────────────────────────────────────────
# Copy the uv binary directly from Astral's official image.
# This is faster than pip-installing uv inside the container.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# ── Working directory ─────────────────────────────────────────────────────────
WORKDIR /app

# ── Install dependencies (cached layer) ───────────────────────────────────────
# Copy only the lock files first.
# Docker caches this layer and skips reinstalling when only source code changes.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# ── Copy source code ──────────────────────────────────────────────────────────
COPY . .

# Install the project package itself (source_code, services, apps).
RUN uv sync --frozen --no-dev

# ── Runtime directories ───────────────────────────────────────────────────────
# Create all artifact folders so they exist even without a mounted volume.
# When volumes ARE mounted (see docker-compose.yml), these are overridden.
RUN mkdir -p \
    data/raw \
    data/processed \
    data/vectorstore \
    models \
    logs \
    deployed

# ── Port ──────────────────────────────────────────────────────────────────────
EXPOSE 8000

# ── Start the FastAPI server ───────────────────────────────────────────────────
CMD ["uv", "run", "api"]
