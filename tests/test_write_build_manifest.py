"""Tests for scripts/write_build_manifest.py (#5319)."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from scripts.write_build_manifest import build_manifest, main

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas" / "build-manifest.schema.json").read_text(encoding="utf-8"))


def test_build_manifest_matches_schema() -> None:
    payload = build_manifest()
    jsonschema.validate(payload, SCHEMA)


def test_write_manifest_cli_writes_valid_json(tmp_path: Path) -> None:
    out = tmp_path / "build-manifest.json"
    assert main(["--out", str(out)]) == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    jsonschema.validate(payload, SCHEMA)


def test_build_manifest_reads_the_given_repo_root(tmp_path: Path) -> None:
    """Every field comes from ``repo_root``, including the commit, so a checkout can be audited."""
    import subprocess

    (tmp_path / ".quarto-version").write_text("9.9.9\n", encoding="utf-8")
    (tmp_path / "requirements-docker.lock").write_text("pkg==1\n", encoding="utf-8")
    (tmp_path / "package-lock.json").write_text("{}\n", encoding="utf-8")
    git = ["git", "-C", str(tmp_path), "-c", "user.name=t", "-c", "user.email=t@example.invalid"]
    subprocess.run([*git, "init", "-q"], check=True)
    subprocess.run([*git, "add", "."], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "init"], check=True)
    head = subprocess.run(
        [*git, "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()

    payload = build_manifest(tmp_path)

    assert payload["git_commit"] == head
    assert payload["quarto_version"] == "9.9.9"
    jsonschema.validate(payload, SCHEMA)


def test_check_flags_a_stale_manifest(tmp_path: Path) -> None:
    out = tmp_path / "build-manifest.json"
    assert main(["--out", str(out)]) == 0
    stale = json.loads(out.read_text(encoding="utf-8"))
    stale["npm_lock_sha256"] = "0" * 64
    out.write_text(json.dumps(stale), encoding="utf-8")
    assert main(["--out", str(out), "--check"]) == 1
    assert main(["--out", str(tmp_path / "missing.json"), "--check"]) == 1
