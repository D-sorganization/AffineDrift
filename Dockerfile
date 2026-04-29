# AffineDrift — reproducible build and dev environment
#
# Stages:
#   base     — Python 3.12 + Quarto + Node.js system dependencies
#   dev      — full dev/test environment (default for `docker run`)
#   builder  — renders the Quarto site to docs/
#   runtime  — minimal static-file server (production)
#
# Usage:
#   docker build --target dev -t affinedrift:dev .
#   docker run --rm affinedrift:dev                    # runs pytest
#   docker run --rm affinedrift:dev npm test           # runs Jest
#   docker build -t affinedrift:latest .               # production serve
#   docker run -p 8080:8000 affinedrift:latest

ARG QUARTO_VERSION=1.6.39
ARG NODE_MAJOR=20
ARG PYTHON_VERSION=3.12

# ---------------------------------------------------------------------------
# base: system deps shared by all stages
# ---------------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS base

ARG QUARTO_VERSION
ARG NODE_MAJOR

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install Quarto + Node.js (LTS) + curl/wget
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg \
    # Quarto
    && curl -fsSL -o /tmp/quarto.deb \
        "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.deb" \
    && apt-get install -y --no-install-recommends /tmp/quarto.deb \
    && rm /tmp/quarto.deb \
    # Node.js LTS via NodeSource
    && curl -fsSL "https://deb.nodesource.com/setup_${NODE_MAJOR}.x" | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# ---------------------------------------------------------------------------
# dev: installs all Python + JS deps, default CMD runs pytest
# ---------------------------------------------------------------------------
FROM base AS dev

# Python dependencies
COPY requirements.txt pyproject.toml ./
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

# Node.js dependencies
COPY package.json package-lock.json ./
RUN npm ci --prefer-offline

# Copy source (after deps so layer cache is warm for code-only changes)
COPY . .

# Default: run pytest (mirrors CI quality gate)
CMD ["python", "-m", "pytest", "--cov=src", "--cov-fail-under=50", "-v"]

# ---------------------------------------------------------------------------
# builder: renders Quarto site to docs/
# ---------------------------------------------------------------------------
FROM base AS builder

COPY requirements.txt pyproject.toml ./
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY package.json package-lock.json ./
RUN npm ci --prefer-offline

COPY . .
RUN rm -f .env .env.local \
    && quarto render . --to html

# ---------------------------------------------------------------------------
# runtime: minimal production image — serves the rendered site
# ---------------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS runtime

WORKDIR /site

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AFFINEDRIFT_PORT=8000

RUN addgroup --system affinedrift \
    && adduser --system --ingroup affinedrift --home /site affinedrift

COPY --from=builder --chown=affinedrift:affinedrift /workspace/docs/ /site/

USER affinedrift

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"AFFINEDRIFT_PORT\", \"8000\")}/index.html', timeout=3).read(1)"

CMD ["sh", "-c", "python -m http.server \"$AFFINEDRIFT_PORT\" --bind 0.0.0.0 --directory /site"]
