from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_uses_multistage_python_312_runtime() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "AS builder" in dockerfile
    assert "AS runtime" in dockerfile
    assert "python:3.12-slim" in dockerfile or "python:${PYTHON_VERSION}-slim" in dockerfile
    assert "QUARTO_VERSION=1.6.39" in dockerfile
    assert "python -m pip install --no-cache-dir -r requirements.txt" in dockerfile
    assert "quarto render . --to html" in dockerfile
    assert (
        "COPY --from=builder --chown=affinedrift:affinedrift /workspace/docs/ /site/" in dockerfile
    )


def test_dockerfile_runs_as_non_root_static_server() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "adduser --system --ingroup affinedrift --home /site affinedrift" in dockerfile
    assert "USER affinedrift" in dockerfile
    assert "EXPOSE 8000" in dockerfile
    assert "python -m http.server" in dockerfile
    assert "--directory /site" in dockerfile
    assert "HEALTHCHECK" in dockerfile


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
