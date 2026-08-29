"""Contracts for the immutable UpstreamDrift companion-manifest consumer."""

from __future__ import annotations

import copy
import hashlib
import json
import os
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path

import pytest

from src.companion.manifest_consumer import (
    MAX_LOCK_BYTES,
    MAX_MANIFEST_BYTES,
    CompanionConsumer,
    CompanionImportError,
    CompanionPin,
    FetchedPayload,
    HttpFetcher,
    validate_lock,
)

ROOT = Path(__file__).resolve().parents[1]
LOCK_SCHEMA = ROOT / "schemas/upstreamdrift-companion-lock-v1.schema.json"
CANONICAL_ROOT = ROOT / "data/upstreamdrift_companion"
PROVIDER_SCHEMA_ID = "https://upstreamdrift.dev/schemas/upstreamdrift-companion-v1.schema.json"


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def _digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _schema_bytes() -> bytes:
    return _json_bytes(
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": PROVIDER_SCHEMA_ID,
            "type": "object",
            "additionalProperties": False,
            "required": ["$schema", "schema_version", "manifest_id", "source", "value"],
            "properties": {
                "$schema": {"const": PROVIDER_SCHEMA_ID},
                "schema_version": {"const": "1.0.0"},
                "manifest_id": {"const": "upstreamdrift-companion"},
                "source": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["repository", "commit"],
                    "properties": {
                        "repository": {"const": "https://github.com/D-sorganization/UpstreamDrift"},
                        "commit": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
                    },
                },
                "value": {"type": "integer"},
            },
        }
    )


def _manifest_bytes(commit: str, *, value: int = 1) -> bytes:
    return _json_bytes(
        {
            "$schema": PROVIDER_SCHEMA_ID,
            "schema_version": "1.0.0",
            "manifest_id": "upstreamdrift-companion",
            "source": {
                "repository": "https://github.com/D-sorganization/UpstreamDrift",
                "commit": commit,
            },
            "value": value,
        }
    )


def _pin(commit: str, manifest: bytes, schema: bytes) -> CompanionPin:
    raw_root = "https://raw.githubusercontent.com/D-sorganization/UpstreamDrift"
    return CompanionPin(
        provider_host="github.com",
        provider_repository="D-sorganization/UpstreamDrift",
        commit=commit,
        manifest_sha256=_digest(manifest),
        schema_sha256=_digest(schema),
        acquisition="immutable-url",
        manifest_provider_path="dist/companion/upstreamdrift-companion.v1.json",
        generator_command=(
            "python -m scripts.companion_catalog --output "
            "dist/companion/upstreamdrift-companion.v1.json"
        ),
        manifest_url=(f"{raw_root}/{commit}/dist/companion/upstreamdrift-companion.v1.json"),
        schema_url=(
            f"{raw_root}/{commit}/docs/api/contracts/" "upstreamdrift-companion-v1.schema.json"
        ),
    )


def _tree_bytes(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_install_is_strict_deterministic_and_verifiable(tmp_path: Path) -> None:
    commit = "1" * 40
    schema = _schema_bytes()
    manifest = _manifest_bytes(commit)
    consumer = CompanionConsumer(tmp_path, LOCK_SCHEMA)

    installed = consumer.install(_pin(commit, manifest, schema), manifest, schema)
    verified = consumer.verify_active()

    assert installed == verified
    assert installed.commit == commit
    assert installed.manifest["manifest_id"] == "upstreamdrift-companion"
    assert installed.snapshot_dir == tmp_path / "snapshots" / commit
    assert (installed.snapshot_dir / "upstreamdrift-companion.v1.json").read_bytes() == manifest
    assert (
        installed.snapshot_dir / "upstreamdrift-companion-v1.schema.json"
    ).read_bytes() == schema
    provenance = (installed.snapshot_dir / "provenance.qmd").read_text(encoding="utf-8")
    assert commit in provenance
    assert _digest(manifest) in provenance
    assert "python -m scripts.companion_catalog --output" in provenance
    assert "immutable-url" in provenance
    assert "does not grant scientific qualification" in provenance


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda pin: replace(pin, provider_host="example.com"), "provider host"),
        (
            lambda pin: replace(pin, provider_repository="someone/UpstreamDrift"),
            "provider repository",
        ),
        (lambda pin: replace(pin, commit="main"), "exact 40-character commit"),
        (
            lambda pin: replace(pin, manifest_url=pin.manifest_url.replace(pin.commit, "main")),
            "mutable branch",
        ),
        (
            lambda pin: replace(
                pin,
                schema_url=pin.schema_url.replace(
                    "docs/api/contracts/", "docs/api/contracts/../private/"
                ),
            ),
            "path traversal",
        ),
        (
            lambda pin: replace(
                pin,
                schema_url=pin.schema_url.replace(
                    "raw.githubusercontent.com", "raw.githubusercontent.com:invalid"
                ),
            ),
            "URL is malformed",
        ),
        (
            lambda pin: replace(pin, generator_command="python `unreviewed`"),
            "generator command",
        ),
    ],
)
def test_pin_rejects_wrong_authority_mutability_and_traversal(
    tmp_path: Path,
    mutation: Callable[[CompanionPin], CompanionPin],
    message: str,
) -> None:
    commit = "1" * 40
    schema = _schema_bytes()
    manifest = _manifest_bytes(commit)
    pin = mutation(_pin(commit, manifest, schema))

    with pytest.raises(CompanionImportError, match=message):
        CompanionConsumer(tmp_path, LOCK_SCHEMA).install(pin, manifest, schema)


@pytest.mark.parametrize(
    ("kind", "message"),
    [
        ("manifest_digest", "manifest SHA-256"),
        ("schema_digest", "schema SHA-256"),
        ("embedded_commit", "embedded commit"),
        ("embedded_repository", "embedded repository"),
        ("schema_id", "provider schema"),
    ],
)
def test_payload_rejects_wrong_digest_commit_schema_and_provider(
    tmp_path: Path, kind: str, message: str
) -> None:
    commit = "1" * 40
    schema = _schema_bytes()
    manifest = _manifest_bytes(commit)
    pin = _pin(commit, manifest, schema)

    if kind == "manifest_digest":
        pin = replace(pin, manifest_sha256="2" * 64)
    elif kind == "schema_digest":
        pin = replace(pin, schema_sha256="2" * 64)
    elif kind == "embedded_commit":
        manifest = _manifest_bytes("2" * 40)
        pin = replace(pin, manifest_sha256=_digest(manifest))
    elif kind == "embedded_repository":
        payload = json.loads(manifest)
        payload["source"]["repository"] = "https://github.com/someone/UpstreamDrift"
        manifest = _json_bytes(payload)
        pin = replace(pin, manifest_sha256=_digest(manifest))
    else:
        schema_payload = json.loads(schema)
        schema_payload["$id"] = "https://example.com/not-provider.json"
        schema = _json_bytes(schema_payload)
        pin = replace(pin, schema_sha256=_digest(schema))

    with pytest.raises(CompanionImportError, match=message):
        CompanionConsumer(tmp_path, LOCK_SCHEMA).install(pin, manifest, schema)


def test_payload_size_limits_fail_before_any_write(tmp_path: Path) -> None:
    commit = "1" * 40
    schema = _schema_bytes()
    manifest = b"x" * (4 * 1024 * 1024 + 1)
    pin = _pin(commit, manifest, schema)

    with pytest.raises(CompanionImportError, match="manifest exceeds"):
        CompanionConsumer(tmp_path, LOCK_SCHEMA).install(pin, manifest, schema)

    assert list(tmp_path.iterdir()) == []


def test_manifest_rejects_duplicate_json_keys(tmp_path: Path) -> None:
    commit = "1" * 40
    schema = _schema_bytes()
    manifest = _manifest_bytes(commit).replace(
        b"{\n", b'{\n  "manifest_id": "shadowed-value",\n', 1
    )

    with pytest.raises(CompanionImportError, match="duplicate key: manifest_id"):
        CompanionConsumer(tmp_path, LOCK_SCHEMA).install(
            _pin(commit, manifest, schema), manifest, schema
        )


class _FakeFetcher:
    def __init__(self, responses: dict[str, FetchedPayload]) -> None:
        self.responses = responses

    def fetch(self, url: str, max_bytes: int) -> FetchedPayload:
        payload = self.responses[url]
        assert len(payload.data) <= max_bytes
        return payload


class _FakeResponse:
    def __init__(self, payload: bytes, final_url: str) -> None:
        self._payload = payload
        self._offset = 0
        self._final_url = final_url
        self.headers = {"Content-Length": str(len(payload))}

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self, size: int) -> bytes:
        chunk = self._payload[self._offset : self._offset + size]
        self._offset += len(chunk)
        return chunk

    def geturl(self) -> str:
        return self._final_url


def test_http_fetcher_requires_https_and_bounds_streamed_bytes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(CompanionImportError, match="requires HTTPS"):
        HttpFetcher().fetch("file:///untrusted/provider.json", 5)

    url = "https://raw.githubusercontent.com/provider/manifest.json"
    monkeypatch.setattr(
        "src.companion.manifest_consumer.urllib.request.urlopen",
        lambda *_args, **_kwargs: _FakeResponse(b"12345", url),
    )
    fetched = HttpFetcher().fetch(url, 5)
    assert fetched == FetchedPayload(data=b"12345", final_url=url)

    monkeypatch.setattr(
        "src.companion.manifest_consumer.urllib.request.urlopen",
        lambda *_args, **_kwargs: _FakeResponse(b"123456", url),
    )
    with pytest.raises(CompanionImportError, match="remote payload exceeds"):
        HttpFetcher().fetch(url, 5)


def test_redirect_escape_is_rejected_before_install(tmp_path: Path) -> None:
    commit = "1" * 40
    schema = _schema_bytes()
    manifest = _manifest_bytes(commit)
    pin = _pin(commit, manifest, schema)
    fetcher = _FakeFetcher(
        {
            pin.manifest_url: FetchedPayload(manifest, "https://evil.example/payload.json"),
            pin.schema_url: FetchedPayload(schema, pin.schema_url),
        }
    )

    with pytest.raises(CompanionImportError, match="redirect escaped"):
        CompanionConsumer(tmp_path, LOCK_SCHEMA).install_from_urls(pin, fetcher)

    assert list(tmp_path.iterdir()) == []


def test_local_export_records_truthful_acquisition_without_false_url(tmp_path: Path) -> None:
    commit = "1" * 40
    schema = _schema_bytes()
    manifest = _manifest_bytes(commit)
    pin = replace(
        _pin(commit, manifest, schema),
        acquisition="protected-local-export",
        manifest_url=None,
        generator_command=(
            "python -m scripts.companion_catalog --output "
            "dist/companion/upstreamdrift-companion.v1.json"
        ),
    )
    consumer = CompanionConsumer(tmp_path, LOCK_SCHEMA)

    installed = consumer.install(pin, manifest, schema)

    provider = installed.lock["provider"]
    assert isinstance(provider, dict)
    assert provider["manifest_acquisition"] == "protected-local-export"
    assert provider["manifest_url"] is None
    assert provider["manifest_provider_path"] == ("dist/companion/upstreamdrift-companion.v1.json")
    provenance = (installed.snapshot_dir / "provenance.qmd").read_text(encoding="utf-8")
    assert "reviewed protected local export (no manifest URL)" in provenance
    with pytest.raises(CompanionImportError, match="URL install requires"):
        consumer.install_from_urls(pin, _FakeFetcher({}))


def test_existing_commit_with_different_bytes_is_a_hard_conflict(tmp_path: Path) -> None:
    commit = "1" * 40
    schema = _schema_bytes()
    first = _manifest_bytes(commit, value=1)
    second = _manifest_bytes(commit, value=2)
    consumer = CompanionConsumer(tmp_path, LOCK_SCHEMA)
    consumer.install(_pin(commit, first, schema), first, schema)
    before = _tree_bytes(tmp_path)

    with pytest.raises(CompanionImportError, match="existing immutable snapshot conflicts"):
        consumer.install(_pin(commit, second, schema), second, schema)

    assert _tree_bytes(tmp_path) == before


def test_partial_atomic_failure_rolls_back_every_new_byte(tmp_path: Path) -> None:
    first_commit = "1" * 40
    second_commit = "2" * 40
    schema = _schema_bytes()
    first = _manifest_bytes(first_commit)
    second = _manifest_bytes(second_commit)
    consumer = CompanionConsumer(tmp_path, LOCK_SCHEMA)
    consumer.install(_pin(first_commit, first, schema), first, schema)
    before = _tree_bytes(tmp_path)
    calls = 0

    def fail_lock_swap(source: Path, destination: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected lock swap failure")
        os.replace(source, destination)

    failing = CompanionConsumer(tmp_path, LOCK_SCHEMA, replace=fail_lock_swap)
    with pytest.raises(CompanionImportError, match="atomic install failed"):
        failing.install(_pin(second_commit, second, schema), second, schema)

    assert _tree_bytes(tmp_path) == before
    assert consumer.verify_active().commit == first_commit


def test_partial_staging_write_failure_leaves_no_new_byte(tmp_path: Path) -> None:
    commit = "1" * 40
    schema = _schema_bytes()
    manifest = _manifest_bytes(commit)
    calls = 0

    def fail_second_write(path: Path, payload: bytes) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected staging write failure")
        path.write_bytes(payload)

    consumer = CompanionConsumer(tmp_path, LOCK_SCHEMA, write_bytes=fail_second_write)
    with pytest.raises(CompanionImportError, match="atomic install failed"):
        consumer.install(_pin(commit, manifest, schema), manifest, schema)

    assert _tree_bytes(tmp_path) == {}


def test_update_check_is_read_only_and_reports_exact_change(tmp_path: Path) -> None:
    first_commit = "1" * 40
    second_commit = "2" * 40
    schema = _schema_bytes()
    first = _manifest_bytes(first_commit)
    second = _manifest_bytes(second_commit)
    consumer = CompanionConsumer(tmp_path, LOCK_SCHEMA)
    consumer.install(_pin(first_commit, first, schema), first, schema)
    before = _tree_bytes(tmp_path)

    result = consumer.check_update(_pin(second_commit, second, schema), second, schema)

    assert result.current_commit == first_commit
    assert result.candidate_commit == second_commit
    assert result.update_available is True
    assert result.manifest_changed is True
    assert _tree_bytes(tmp_path) == before


def test_update_check_rejects_same_commit_with_different_bytes(tmp_path: Path) -> None:
    commit = "1" * 40
    schema = _schema_bytes()
    first = _manifest_bytes(commit, value=1)
    second = _manifest_bytes(commit, value=2)
    consumer = CompanionConsumer(tmp_path, LOCK_SCHEMA)
    consumer.install(_pin(commit, first, schema), first, schema)
    before = _tree_bytes(tmp_path)

    with pytest.raises(CompanionImportError, match="reuses an immutable commit"):
        consumer.check_update(_pin(commit, second, schema), second, schema)

    assert _tree_bytes(tmp_path) == before


def test_provider_schema_rejects_external_references(tmp_path: Path) -> None:
    commit = "1" * 40
    schema_payload = json.loads(_schema_bytes())
    schema_payload["$defs"] = {"remote": {"$ref": "https://evil.example/schema.json"}}
    schema = _json_bytes(schema_payload)
    manifest = _manifest_bytes(commit)

    with pytest.raises(CompanionImportError, match="external reference"):
        CompanionConsumer(tmp_path, LOCK_SCHEMA).install(
            _pin(commit, manifest, schema), manifest, schema
        )


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (
            lambda lock: lock["provider"].__setitem__(
                "manifest_bytes", lock["provider"]["manifest_bytes"] + 1
            ),
            "manifest byte count",
        ),
        (
            lambda lock: lock["snapshot"].__setitem__("directory", f"snapshots/{'2' * 40}"),
            "snapshot directory does not match the provider commit",
        ),
        (
            lambda lock: lock["provider"].__setitem__(
                "schema_url",
                (
                    "https://raw.githubusercontent.com/D-sorganization/UpstreamDrift/"
                    f"{'1' * 40}/docs/api/contracts/not-the-provider-schema.json"
                ),
            ),
            "schema URL path is invalid",
        ),
        (
            lambda lock: lock["provider"].__setitem__(
                "revision_url",
                f"https://github.com/D-sorganization/UpstreamDrift/tree/{'2' * 40}",
            ),
            "revision URL does not match",
        ),
    ],
)
def test_verify_rejects_tampered_lock_metadata(
    tmp_path: Path, mutation: Callable[[dict[str, object]], None], message: str
) -> None:
    commit = "1" * 40
    schema = _schema_bytes()
    manifest = _manifest_bytes(commit)
    consumer = CompanionConsumer(tmp_path, LOCK_SCHEMA)
    installed = consumer.install(_pin(commit, manifest, schema), manifest, schema)
    lock = copy.deepcopy(installed.lock)
    mutation(lock)
    consumer.lock_path.write_bytes(_json_bytes(lock))

    with pytest.raises(CompanionImportError, match=message):
        consumer.verify_active()


def test_lock_schema_is_strict_and_versioned(tmp_path: Path) -> None:
    commit = "1" * 40
    schema = _schema_bytes()
    manifest = _manifest_bytes(commit)
    installed = CompanionConsumer(tmp_path, LOCK_SCHEMA).install(
        _pin(commit, manifest, schema), manifest, schema
    )
    lock = copy.deepcopy(installed.lock)
    lock["undeclared"] = True

    with pytest.raises(CompanionImportError, match="Additional properties"):
        validate_lock(lock, LOCK_SCHEMA)


def test_active_lock_rejects_duplicate_json_keys(tmp_path: Path) -> None:
    commit = "1" * 40
    schema = _schema_bytes()
    manifest = _manifest_bytes(commit)
    consumer = CompanionConsumer(tmp_path, LOCK_SCHEMA)
    consumer.install(_pin(commit, manifest, schema), manifest, schema)
    duplicate = consumer.lock_path.read_bytes().replace(
        b"{\n",
        b'{\n  "schema_version": "affinedrift/upstreamdrift-companion-lock/v1",\n',
        1,
    )
    consumer.lock_path.write_bytes(duplicate)

    with pytest.raises(CompanionImportError, match="duplicate key: schema_version"):
        consumer.verify_active()


def test_verify_rejects_unexpected_snapshot_entries(tmp_path: Path) -> None:
    commit = "1" * 40
    schema = _schema_bytes()
    manifest = _manifest_bytes(commit)
    consumer = CompanionConsumer(tmp_path, LOCK_SCHEMA)
    installed = consumer.install(_pin(commit, manifest, schema), manifest, schema)
    (installed.snapshot_dir / "undeclared").mkdir()

    with pytest.raises(CompanionImportError, match="snapshot entries"):
        consumer.verify_active()


def test_verify_bounds_active_manifest_before_parsing(tmp_path: Path) -> None:
    commit = "1" * 40
    schema = _schema_bytes()
    manifest = _manifest_bytes(commit)
    consumer = CompanionConsumer(tmp_path, LOCK_SCHEMA)
    installed = consumer.install(_pin(commit, manifest, schema), manifest, schema)
    (installed.snapshot_dir / "upstreamdrift-companion.v1.json").write_bytes(
        b"x" * (MAX_MANIFEST_BYTES + 1)
    )

    with pytest.raises(CompanionImportError, match="manifest exceeds"):
        consumer.verify_active()


def test_verify_bounds_active_lock_before_parsing(tmp_path: Path) -> None:
    commit = "1" * 40
    schema = _schema_bytes()
    manifest = _manifest_bytes(commit)
    consumer = CompanionConsumer(tmp_path, LOCK_SCHEMA)
    consumer.install(_pin(commit, manifest, schema), manifest, schema)
    consumer.lock_path.write_bytes(b" " * (MAX_LOCK_BYTES + 1))

    with pytest.raises(CompanionImportError, match="active lock exceeds"):
        consumer.verify_active()


def test_canonical_snapshot_is_exact_verified_and_explicitly_draft() -> None:
    """Keep the checked-in provider snapshot exact without promoting its authority."""
    installed = CompanionConsumer(CANONICAL_ROOT, LOCK_SCHEMA).verify_active()
    provider = installed.lock["provider"]
    publication = installed.lock["publication"]
    manifest = installed.manifest

    assert manifest["manifest_id"] == "upstreamdrift-companion"
    assert manifest["source"]["repository"] == ("https://github.com/D-sorganization/UpstreamDrift")
    assert manifest["source"]["commit"] == installed.commit
    assert provider["manifest_acquisition"] == "protected-local-export"
    assert provider["manifest_url"] is None
    assert publication["state"] == "draft"
    assert manifest["publication"]["state"] == "draft"
    assert manifest["publication"]["blockers"]
    assert manifest["programs"]
    assert manifest["features"]
    assert manifest["engines"]
    assert manifest["workflows"] == []
    assert manifest["screenshots"] == []
    assert manifest["documentation"] == []
