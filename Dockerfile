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

ARG PYTHON_BASE_IMAGE=python:3.12-slim@sha256:46cb7cc2877e60fbd5e21a9ae6115c30ace7a077b9f8772da879e4590c18c2e3
ARG NODE_MAJOR=20
ARG QUARTO_VERSION=1.6.39
ARG QUARTO_DEB_SHA256=cf3f2840d54149aac0a2f68e8d53b6e3122d2a5dae0cb9c09a26fe9eb9ae5d86
ARG AFFINEDRIFT_GIT_SHA=unknown

# ---------------------------------------------------------------------------
# base: system deps shared by all stages
# ---------------------------------------------------------------------------
FROM ${PYTHON_BASE_IMAGE} AS base

ARG AFFINEDRIFT_GIT_SHA
ARG QUARTO_VERSION
ARG QUARTO_DEB_SHA256
ARG NODE_MAJOR

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    QUARTO_VERSION=${QUARTO_VERSION} \
    QUARTO_DEB_SHA256=${QUARTO_DEB_SHA256} \
    AFFINEDRIFT_GIT_SHA=${AFFINEDRIFT_GIT_SHA}

# Install Quarto + Node.js (LTS) using verified artifacts.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg \
    && install -d -m 0755 /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
        | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODE_MAJOR}.x nodistro main" \
        > /etc/apt/sources.list.d/nodesource.list \
    && curl -fsSL -o /tmp/quarto.deb \
        "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.deb" \
    && echo "${QUARTO_DEB_SHA256}  /tmp/quarto.deb" | sha256sum -c - \
    && apt-get update \
    && apt-get install -y --no-install-recommends /tmp/quarto.deb nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# ---------------------------------------------------------------------------
# dev: installs all Python + JS deps, default CMD runs pytest
# ---------------------------------------------------------------------------
FROM base AS dev

# Python dependencies
COPY requirements.txt requirements-docker.lock pyproject.toml ./
RUN python -m pip install --require-hashes -r requirements-docker.lock \
    && sha256sum requirements-docker.lock | awk '{print $1}' > /tmp/python-lock.sha256

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

COPY requirements.txt requirements-docker.lock pyproject.toml ./
RUN python -m pip install --require-hashes -r requirements-docker.lock \
    && sha256sum requirements-docker.lock | awk '{print $1}' > /tmp/python-lock.sha256

COPY package.json package-lock.json ./
RUN npm ci --prefer-offline

COPY . .
RUN rm -f .env .env.local \
    && quarto render . --to html \
    && find docs -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | awk '{print $1}' > /tmp/site.sha256 \
    && python -c "import json, os, pathlib; provenance = {'git_commit': os.environ.get('AFFINEDRIFT_GIT_SHA', 'unknown'), 'quarto_version': os.environ['QUARTO_VERSION'], 'quarto_deb_sha256': os.environ['QUARTO_DEB_SHA256'], 'python_lock_file': 'requirements-docker.lock', 'python_lock_sha256': pathlib.Path('/tmp/python-lock.sha256').read_text(encoding='utf-8').strip(), 'site_sha256': pathlib.Path('/tmp/site.sha256').read_text(encoding='utf-8').strip()}; pathlib.Path('docs/build-provenance.json').write_text(json.dumps(provenance, indent=2) + '\\n', encoding='utf-8')"

# ---------------------------------------------------------------------------
# runtime: minimal production image — serves the rendered site
# ---------------------------------------------------------------------------
FROM ${PYTHON_BASE_IMAGE} AS runtime

ARG AFFINEDRIFT_GIT_SHA
ARG QUARTO_VERSION
ARG QUARTO_DEB_SHA256

LABEL org.opencontainers.image.revision="${AFFINEDRIFT_GIT_SHA}" \
      org.opencontainers.image.version="${QUARTO_VERSION}" \
      org.opencontainers.image.base.digest="sha256:46cb7cc2877e60fbd5e21a9ae6115c30ace7a077b9f8772da879e4590c18c2e3" \
      org.affinedrift.quarto.deb-sha256="${QUARTO_DEB_SHA256}"

WORKDIR /site

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AFFINEDRIFT_PORT=8000

RUN addgroup --system affinedrift \
    && adduser --system --ingroup affinedrift --home /site affinedrift

COPY --from=builder --chown=affinedrift:affinedrift /workspace/docs/ /site/
COPY --from=builder --chown=affinedrift:affinedrift /workspace/docs/build-provenance.json /site/build-provenance.json

USER affinedrift

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"AFFINEDRIFT_PORT\", \"8000\")}/index.html', timeout=3).read(1)"

CMD ["sh", "-c", "python -m http.server \"$AFFINEDRIFT_PORT\" --bind 0.0.0.0 --directory /site"]
