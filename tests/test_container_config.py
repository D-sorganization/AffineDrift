from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_uses_multistage_python_312_runtime() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "AS builder" in dockerfile
    assert "AS runtime" in dockerfile
    assert (
        "python:3.12-slim@sha256:46cb7cc2877e60fbd5e21a9ae6115c30ace7a077b9f8772da879e4590c18c2e3"
        in dockerfile
    )
    assert "QUARTO_VERSION=1.6.39" in dockerfile
    assert (
        "QUARTO_DEB_SHA256=cf3f2840d54149aac0a2f68e8d53b6e3122d2a5dae0cb9c09a26fe9eb9ae5d86"
        in dockerfile
    )
    assert "python -m pip install --require-hashes -r requirements-docker.lock" in dockerfile
    assert "quarto render . --to html" in dockerfile
    assert (
        "COPY --from=builder --chown=affinedrift:affinedrift /workspace/docs/ /site/" in dockerfile
    )


def test_dockerfile_verifies_downloaded_build_inputs() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert 'echo "${QUARTO_DEB_SHA256}  /tmp/quarto.deb" | sha256sum -c -' in dockerfile
    assert "signed-by=/etc/apt/keyrings/nodesource.gpg" in dockerfile
    assert (
        'curl -fsSL "https://deb.nodesource.com/setup_${NODE_MAJOR}.x" | bash -' not in dockerfile
    )
    assert "COPY requirements.txt requirements-docker.lock pyproject.toml ./" in dockerfile


def test_dockerfile_runs_as_non_root_static_server() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "adduser --system --ingroup affinedrift --home /site affinedrift" in dockerfile
    assert "USER affinedrift" in dockerfile
    assert "EXPOSE 8000" in dockerfile
    assert "python -m http.server" in dockerfile
    assert "--directory /site" in dockerfile
    assert "HEALTHCHECK" in dockerfile
    assert "/site/build-provenance.json" in dockerfile


def test_compose_hardens_local_preview_service() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    assert "8080:8000" in compose
    assert "read_only: true" in compose
    assert "no-new-privileges:true" in compose
    assert "AFFINEDRIFT_PORT: 8000" in compose
    assert "healthcheck:" in compose


def test_readme_documents_docker_usage_and_secret_handling() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "docker build -t affinedrift:local ." in readme
    assert "docker run --rm -p 8080:8000 affinedrift:local" in readme
    assert "docker compose up --build" in readme
    assert "do not bake secrets into the image" in readme
