FROM python:3.12-slim AS builder

ARG QUARTO_VERSION=1.6.39

WORKDIR /workspace

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && curl -fsSL -o /tmp/quarto.deb "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.deb" \
    && apt-get install -y --no-install-recommends /tmp/quarto.deb \
    && rm -rf /var/lib/apt/lists/* /tmp/quarto.deb

COPY requirements.txt pyproject.toml ./
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY . .
RUN rm -f .env .env.local \
    && quarto render . --to html

FROM python:3.12-slim AS runtime

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
