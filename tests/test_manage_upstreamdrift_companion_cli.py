"""CLI contracts for explicit immutable companion installation and checking."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.manage_upstreamdrift_companion import main

from .test_upstreamdrift_companion_consumer import _manifest_bytes, _schema_bytes

ROOT = Path(__file__).resolve().parents[1]
LOCK_SCHEMA = ROOT / "schemas/upstreamdrift-companion-lock-v1.schema.json"


def _digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _local_args(
    command: str,
    root: Path,
    commit: str,
    manifest: Path,
    schema: Path,
    *,
    manifest_digest: str,
    schema_digest: str,
) -> list[str]:
    raw_schema = (
        "https://raw.githubusercontent.com/D-sorganization/UpstreamDrift/"
        f"{commit}/docs/api/contracts/upstreamdrift-companion-v1.schema.json"
    )
    return [
        "--root",
        str(root),
        "--lock-schema",
        str(LOCK_SCHEMA),
        command,
        "--commit",
        commit,
        "--manifest-sha256",
        manifest_digest,
        "--schema-sha256",
        schema_digest,
        "--schema-url",
        raw_schema,
        "--generator-command",
        (
            "python -m scripts.companion_catalog --output "
            "dist/companion/upstreamdrift-companion.v1.json"
        ),
        "--manifest",
        str(manifest),
        "--schema",
        str(schema),
    ]


def test_cli_installs_and_verifies_local_export(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    commit = "1" * 40
    manifest_bytes = _manifest_bytes(commit)
    schema_bytes = _schema_bytes()
    manifest = tmp_path / "provider-manifest.json"
    schema = tmp_path / "provider-schema.json"
    manifest.write_bytes(manifest_bytes)
    schema.write_bytes(schema_bytes)
    root = tmp_path / "consumer"

    assert (
        main(
            _local_args(
                "install-local",
                root,
                commit,
                manifest,
                schema,
                manifest_digest=_digest(manifest_bytes),
                schema_digest=_digest(schema_bytes),
            )
        )
        == 0
    )
    install_result = json.loads(capsys.readouterr().out)
    assert install_result["commit"] == commit
    assert install_result["verified"] is True

    assert main(["--root", str(root), "--lock-schema", str(LOCK_SCHEMA), "verify"]) == 0
    verify_result = json.loads(capsys.readouterr().out)
    assert verify_result["commit"] == commit


def test_cli_update_check_is_read_only(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    first_commit = "1" * 40
    second_commit = "2" * 40
    schema_bytes = _schema_bytes()
    schema = tmp_path / "provider-schema.json"
    schema.write_bytes(schema_bytes)
    first_bytes = _manifest_bytes(first_commit)
    first = tmp_path / "first.json"
    first.write_bytes(first_bytes)
    root = tmp_path / "consumer"
    install_args = _local_args(
        "install-local",
        root,
        first_commit,
        first,
        schema,
        manifest_digest=_digest(first_bytes),
        schema_digest=_digest(schema_bytes),
    )
    assert main(install_args) == 0
    capsys.readouterr()
    before = {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }

    second_bytes = _manifest_bytes(second_commit)
    second = tmp_path / "second.json"
    second.write_bytes(second_bytes)
    check_args = _local_args(
        "check-local",
        root,
        second_commit,
        second,
        schema,
        manifest_digest=_digest(second_bytes),
        schema_digest=_digest(schema_bytes),
    )
    assert main(check_args) == 0
    result = json.loads(capsys.readouterr().out)
    after = {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }

    assert result["update_available"] is True
    assert result["wrote_files"] is False
    assert before == after


def test_cli_fails_closed_on_unreviewed_digest(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    commit = "1" * 40
    manifest_bytes = _manifest_bytes(commit)
    schema_bytes = _schema_bytes()
    manifest = tmp_path / "provider-manifest.json"
    schema = tmp_path / "provider-schema.json"
    manifest.write_bytes(manifest_bytes)
    schema.write_bytes(schema_bytes)

    result = main(
        _local_args(
            "install-local",
            tmp_path / "consumer",
            commit,
            manifest,
            schema,
            manifest_digest="2" * 64,
            schema_digest=_digest(schema_bytes),
        )
    )

    assert result == 1
    assert capsys.readouterr().out == ""
