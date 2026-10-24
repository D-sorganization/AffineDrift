# Security-scan image for AffineDrift (#5127), in the anthropics/oss-scanner layout.
#
# The scanner builds this file with the repository root as the build context. Network
# access exists only while this file builds; the audit itself runs OFFLINE, so every
# Python and Node dependency the tests need is fetched here.
#
# Source of truth: the repository's own Dockerfile (`dev` stage), requirements-docker.lock
# (hash-pinned, generated from requirements.txt), package-lock.json, .nvmrc and
# .quarto-version. Keep the pins below equal to that Dockerfile's ARGs.
#
# Deliberately skipped: the full `quarto render .` of the site. It renders hundreds of
# pages and takes far longer than the scan budget allows. Quarto itself IS installed, so
# a single page or a single Lua filter can be exercised offline, for example:
#   quarto pandoc -f markdown -t html --lua-filter scripts/filters/term-tooltip.lua in.md
#
# No secrets: the root .dockerignore already drops .git, .github, .env* and *.key.

# Debian (bookworm) based; same digest-pinned base as the repo's Dockerfile.
ARG PYTHON_BASE_IMAGE=python:3.12-slim@sha256:46cb7cc2877e60fbd5e21a9ae6115c30ace7a077b9f8772da879e4590c18c2e3
FROM ${PYTHON_BASE_IMAGE}

ARG NODE_MAJOR=22
ARG QUARTO_VERSION=1.8.26
ARG QUARTO_DEB_SHA256=60451a42095dd60bc23ad529b39ca81017da688aab029bec9b5565818fc55cf8

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    MPLBACKEND=Agg \
    QT_QPA_PLATFORM=offscreen \
    NPM_CONFIG_UPDATE_NOTIFIER=false

# System tools, Node.js (Jest suite for js/) and the verified Quarto .deb (Lua filters).
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates curl gnupg git procps \
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
    && rm -f /tmp/quarto.deb \
    && rm -rf /var/lib/apt/lists/*

# Dependencies first, so a source-only change keeps the layer cache warm.
WORKDIR /src
COPY requirements.txt requirements-docker.lock pyproject.toml /src/
RUN python -m pip install --require-hashes -r /src/requirements-docker.lock
COPY package.json package-lock.json /src/
RUN npm ci --no-audit --no-fund

# scanner contract: the checkout lives inside the image, at /src
COPY . /src
WORKDIR /src

# COPY leaves files world-readable, so the unprivileged sandbox user (uid 65532) can read
# the tree. Open only the top-level directory for writes. A recursive chmod over
# node_modules copies every file up through overlayfs and takes tens of minutes.
RUN chmod a+rwx /src

# Cheap tests, so the image is known to work. Failures never abort the build.
# pytest uses the default offline lane from pyproject.toml (slow, network, e2e and
# live-simulation markers are deselected); coverage is not measured here.
RUN (timeout 1500 python -m pytest tests -q -p no:cacheprovider --maxfail=20 \
        --continue-on-collection-errors \
        || echo "WARNING: pytest reported failures or timed out") \
    && (timeout 600 npx --no-install jest --ci --silent \
        || echo "WARNING: jest reported failures or timed out")

# Phase B runs as uid 65532 (sandbox-forced); never root.
USER 65532:65532
