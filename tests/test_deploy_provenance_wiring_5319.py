"""The deploy workflow must produce and publish the build manifest and SBOM (#5319).

The writers exist (``write_build_manifest`` and ``write_sbom``); this pins that
``deploy-website.yml`` runs them in the build job, verifies them, and publishes
them as a retained workflow artifact, never inside ``_site`` (the public pages).
"""

from __future__ import annotations

from pathlib import Path

import yaml

WORKFLOW = Path(".github/workflows/deploy-website.yml")


def _build_steps() -> list[dict]:
    data = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    return data["jobs"]["build"]["steps"]


def _step_text(step: dict) -> str:
    return f"{step.get('name', '')}\n{step.get('run', '')}\n{step.get('with', '')}"


def _index(steps: list[dict], needle: str) -> int:
    for i, step in enumerate(steps):
        if needle in _step_text(step):
            return i
    raise AssertionError(f"no build step mentions {needle!r}")


def test_build_job_writes_manifest_and_sbom() -> None:
    steps = _build_steps()
    assert _index(steps, "scripts.write_build_manifest") >= 0
    assert _index(steps, "scripts.write_sbom") >= 0


def test_provenance_is_checked_not_only_written() -> None:
    text = "\n".join(_step_text(s) for s in _build_steps())
    assert "scripts.write_build_manifest --check" in text
    assert "scripts.write_sbom --check" in text


def test_provenance_is_written_after_site_output_is_final() -> None:
    steps = _build_steps()
    prune = _index(steps, "prune_internal_docs_from_deploy")
    assert _index(steps, "scripts.write_build_manifest") > prune
    assert _index(steps, "scripts.write_sbom") > prune


def test_provenance_is_published_as_a_retained_artifact_outside_site() -> None:
    steps = _build_steps()
    uploads = [
        s
        for s in steps
        if str(s.get("uses", "")).startswith("actions/upload-artifact")
        and "build-provenance" in str(s.get("with", {}).get("name", ""))
    ]
    assert len(uploads) == 1
    path = str(uploads[0]["with"]["path"])
    assert "build-manifest.json" in path and "sbom.cdx.json" in path
    assert "_site" not in path
    assert int(uploads[0]["with"]["retention-days"]) >= 90
    assert uploads[0].get("if") in (None, "success()", "${{ success() }}")


def test_provenance_files_never_enter_the_public_site() -> None:
    for step in _build_steps():
        run = str(step.get("run", ""))
        if "write_build_manifest" in run or "write_sbom" in run:
            assert "_site" not in run, step.get("name")
