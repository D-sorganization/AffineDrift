"""Strict, immutable consumer for UpstreamDrift companion manifests."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
import urllib.parse
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Protocol, cast

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

LOCK_VERSION = "affinedrift/upstreamdrift-companion-lock/v1"
PROVIDER_HOST = "github.com"
PROVIDER_REPOSITORY = "D-sorganization/UpstreamDrift"
PROVIDER_REPOSITORY_URL = f"https://github.com/{PROVIDER_REPOSITORY}"
PROVIDER_SCHEMA_ID = "https://upstreamdrift.dev/schemas/upstreamdrift-companion-v1.schema.json"
MANIFEST_NAME = "upstreamdrift-companion.v1.json"
PROVIDER_SCHEMA_NAME = "upstreamdrift-companion-v1.schema.json"
PROVENANCE_NAME = "provenance.qmd"
MAX_MANIFEST_BYTES = 4 * 1024 * 1024
MAX_SCHEMA_BYTES = 512 * 1024
_COMMIT = re.compile(r"(?!0{40}$)[0-9a-f]{40}")
_DIGEST = re.compile(r"(?!0{64}$)[0-9a-f]{64}")
_MUTABLE_SEGMENTS = frozenset({"main", "master", "head"})
_APPROVED_REMOTE_PATHS = {
    "manifest": ("dist", "companion", MANIFEST_NAME),
    "schema": ("docs", "api", "contracts", PROVIDER_SCHEMA_NAME),
}
LOCAL_EXPORT = "protected-local-export"
IMMUTABLE_URL = "immutable-url"
MANIFEST_PROVIDER_PATH = "dist/companion/upstreamdrift-companion.v1.json"


class CompanionImportError(RuntimeError):
    """Raised when an immutable companion import cannot prove its contract."""


@dataclass(frozen=True)
class CompanionPin:
    """Caller-reviewed provider identity and byte-level expectations."""

    provider_host: str
    provider_repository: str
    commit: str
    manifest_sha256: str
    schema_sha256: str
    acquisition: str
    manifest_provider_path: str
    generator_command: str
    manifest_url: str | None
    schema_url: str


@dataclass(frozen=True)
class FetchedPayload:
    """Bounded fetched bytes plus the final URL after redirects."""

    data: bytes
    final_url: str


class Fetcher(Protocol):
    """Small download boundary used by the consumer and deterministic tests."""

    def fetch(self, url: str, max_bytes: int) -> FetchedPayload:
        """Fetch at most ``max_bytes`` and report the final URL."""


@dataclass(frozen=True)
class InstalledCompanion:
    """Verified view of the active immutable snapshot."""

    commit: str
    snapshot_dir: Path
    manifest: dict[str, object]
    lock: dict[str, object]


@dataclass(frozen=True)
class UpdateCheck:
    """Read-only comparison between the active and candidate pins."""

    current_commit: str
    candidate_commit: str
    update_available: bool
    manifest_changed: bool
    schema_changed: bool


class HttpFetcher:
    """Bounded HTTPS fetcher; URL authority is rechecked by the consumer."""

    def fetch(self, url: str, max_bytes: int) -> FetchedPayload:
        """Download a bounded payload without trusting redirect destinations."""
        if urllib.parse.urlsplit(url).scheme != "https":
            raise CompanionImportError("provider download requires HTTPS")
        request = urllib.request.Request(  # noqa: S310 -- HTTPS checked above; authority checked by consumer.  # nosec B310
            url, headers={"User-Agent": "AffineDrift/companion-v1"}
        )
        try:
            with urllib.request.urlopen(  # noqa: S310 -- HTTPS and authority are validated before installation.  # nosec B310
                request, timeout=30
            ) as response:
                header = response.headers.get("Content-Length")
                if header is not None and int(header) > max_bytes:
                    raise CompanionImportError(f"remote payload exceeds {max_bytes} bytes")
                with tempfile.TemporaryFile() as temporary:
                    remaining = max_bytes + 1
                    while remaining:
                        chunk = response.read(min(64 * 1024, remaining))
                        if not chunk:
                            break
                        temporary.write(chunk)
                        remaining -= len(chunk)
                    temporary.seek(0)
                    data = temporary.read()
                final_url = response.geturl()
        except (OSError, ValueError) as exc:
            raise CompanionImportError(f"provider download failed: {exc}") from exc
        if len(data) > max_bytes:
            raise CompanionImportError(f"remote payload exceeds {max_bytes} bytes")
        return FetchedPayload(data=data, final_url=final_url)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_object(data: bytes, label: str) -> dict[str, object]:
    try:
        value = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CompanionImportError(f"{label} is not canonical JSON: {exc}") from exc
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise CompanionImportError(f"{label} must be a JSON object")
    return cast(dict[str, object], value)


def _schema_errors(instance: object, schema: object) -> list[str]:
    if not isinstance(schema, dict):
        return ["schema must be an object"]
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.absolute_path))
    return [
        f"{'/'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in errors
    ]


def validate_lock(lock: object, lock_schema_path: Path) -> dict[str, object]:
    """Validate and return one strict AffineDrift companion lock."""
    try:
        schema = json.loads(lock_schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CompanionImportError(f"cannot load lock schema: {exc}") from exc
    errors = _schema_errors(lock, schema)
    if errors:
        raise CompanionImportError("; ".join(errors))
    if not isinstance(lock, dict):
        raise CompanionImportError("lock must be an object")
    return cast(dict[str, object], lock)


def _pin_url(pin: CompanionPin, url: str, kind: str, *, redirected: bool = False) -> None:
    try:
        parsed = urllib.parse.urlsplit(url)
        port = parsed.port
    except ValueError as exc:
        raise CompanionImportError(f"{kind} URL is malformed") from exc
    decoded_path = urllib.parse.unquote(parsed.path)
    path = PurePosixPath(decoded_path)
    if any(part.lower() in _MUTABLE_SEGMENTS for part in path.parts):
        raise CompanionImportError(f"{kind} URL contains a mutable branch")
    if ".." in path.parts or "." in path.parts:
        raise CompanionImportError(f"{kind} URL contains path traversal")
    if (
        parsed.scheme != "https"
        or parsed.hostname != "raw.githubusercontent.com"
        or port is not None
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        label = "redirect escaped approved provider authority" if redirected else "URL authority"
        raise CompanionImportError(f"{kind} {label} is invalid")
    expected = (
        "D-sorganization",
        "UpstreamDrift",
        pin.commit,
        *_APPROVED_REMOTE_PATHS[kind],
    )
    if path.parts[1:] != expected:
        label = "redirect escaped approved provider path" if redirected else "URL path"
        raise CompanionImportError(f"{kind} {label} is invalid")


def _validate_pin_identity(pin: CompanionPin) -> None:
    if pin.provider_host != PROVIDER_HOST:
        raise CompanionImportError("provider host is not allowlisted")
    if pin.provider_repository != PROVIDER_REPOSITORY:
        raise CompanionImportError("provider repository is not allowlisted")
    if _COMMIT.fullmatch(pin.commit) is None:
        raise CompanionImportError("provider revision must be an exact 40-character commit")


def _validate_pin_digests(pin: CompanionPin) -> None:
    if _DIGEST.fullmatch(pin.manifest_sha256) is None:
        raise CompanionImportError("manifest SHA-256 is invalid")
    if _DIGEST.fullmatch(pin.schema_sha256) is None:
        raise CompanionImportError("schema SHA-256 is invalid")


def _validate_acquisition(pin: CompanionPin) -> None:
    if pin.manifest_provider_path != MANIFEST_PROVIDER_PATH:
        raise CompanionImportError("manifest provider path is not approved")
    if (
        not pin.generator_command.strip()
        or "\n" in pin.generator_command
        or "\r" in pin.generator_command
        or "`" in pin.generator_command
    ):
        raise CompanionImportError("manifest generator command is invalid")
    if pin.acquisition == LOCAL_EXPORT:
        if pin.manifest_url is not None:
            raise CompanionImportError("local-export manifest URL must be absent")
    elif pin.acquisition == IMMUTABLE_URL:
        if pin.manifest_url is None:
            raise CompanionImportError("immutable manifest URL is required")
        _pin_url(pin, pin.manifest_url, "manifest")
    else:
        raise CompanionImportError("manifest acquisition mode is unsupported")


def _validate_pin(pin: CompanionPin) -> None:
    _validate_pin_identity(pin)
    _validate_pin_digests(pin)
    _validate_acquisition(pin)
    _pin_url(pin, pin.schema_url, "schema")


def _provider_schema_identity(schema: Mapping[str, object]) -> None:
    if schema.get("$id") != PROVIDER_SCHEMA_ID:
        raise CompanionImportError("provider schema ID is unsupported")
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        raise CompanionImportError("provider schema dialect is unsupported")
    properties = schema.get("properties")
    if not isinstance(properties, dict):
        raise CompanionImportError("provider schema properties are missing")
    schema_version = properties.get("schema_version")
    manifest_id = properties.get("manifest_id")
    if not isinstance(schema_version, dict) or schema_version.get("const") != "1.0.0":
        raise CompanionImportError("provider schema version is unsupported")
    if not isinstance(manifest_id, dict) or manifest_id.get("const") != "upstreamdrift-companion":
        raise CompanionImportError("provider schema manifest ID is unsupported")


def _reject_external_references(value: object) -> None:
    if isinstance(value, dict):
        reference = value.get("$ref")
        if reference is not None and (
            not isinstance(reference, str) or not reference.startswith("#")
        ):
            raise CompanionImportError("provider schema contains an external reference")
        for child in value.values():
            _reject_external_references(child)
    elif isinstance(value, list):
        for child in value:
            _reject_external_references(child)


def _provider_schema_contract(schema: Mapping[str, object]) -> None:
    _provider_schema_identity(schema)
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise CompanionImportError(f"provider schema is invalid: {exc.message}") from exc
    _reject_external_references(schema)


def _embedded_source(manifest: Mapping[str, object]) -> tuple[str, str]:
    source = manifest.get("source")
    if not isinstance(source, dict):
        raise CompanionImportError("manifest source must be an object")
    repository = source.get("repository")
    commit = source.get("commit")
    if not isinstance(repository, str) or not isinstance(commit, str):
        raise CompanionImportError("manifest source identity is incomplete")
    return repository, commit


def _validate_payloads(
    pin: CompanionPin, manifest_bytes: bytes, schema_bytes: bytes
) -> tuple[dict[str, object], dict[str, object]]:
    _validate_pin(pin)
    if len(manifest_bytes) > MAX_MANIFEST_BYTES:
        raise CompanionImportError(f"manifest exceeds {MAX_MANIFEST_BYTES} bytes")
    if len(schema_bytes) > MAX_SCHEMA_BYTES:
        raise CompanionImportError(f"schema exceeds {MAX_SCHEMA_BYTES} bytes")
    if _sha256(manifest_bytes) != pin.manifest_sha256:
        raise CompanionImportError("manifest SHA-256 does not match the reviewed pin")
    if _sha256(schema_bytes) != pin.schema_sha256:
        raise CompanionImportError("schema SHA-256 does not match the reviewed pin")
    schema = _json_object(schema_bytes, "provider schema")
    _provider_schema_contract(schema)
    manifest = _json_object(manifest_bytes, "provider manifest")
    repository, commit = _embedded_source(manifest)
    if repository != PROVIDER_REPOSITORY_URL:
        raise CompanionImportError("embedded repository does not match the allowlisted provider")
    if commit != pin.commit:
        raise CompanionImportError("embedded commit does not match the reviewed pin")
    errors = _schema_errors(manifest, schema)
    if errors:
        raise CompanionImportError("provider manifest violates its schema: " + "; ".join(errors))
    return manifest, schema


def _provenance(pin: CompanionPin) -> bytes:
    acquisition = (
        "reviewed protected local export (no manifest URL)"
        if pin.manifest_url is None
        else pin.manifest_url
    )
    return (
        "<!-- DO NOT EDIT. Generated by the immutable companion consumer. -->\n\n"
        "::: {.provenance-note}\n"
        "## UpstreamDrift Companion Provenance\n\n"
        f"- **Provider:** `{pin.provider_repository}`\n"
        f"- **Protected revision:** `{pin.commit}`\n"
        f"- **Manifest SHA-256:** `{pin.manifest_sha256}`\n"
        f"- **Schema SHA-256:** `{pin.schema_sha256}`\n"
        f"- **Manifest acquisition:** `{pin.acquisition}`\n"
        f"- **Manifest provider path:** `{pin.manifest_provider_path}`\n"
        f"- **Acquisition location:** `{acquisition}`\n"
        f"- **Provider generator:** `{pin.generator_command}`\n"
        f"- **Immutable schema URL:** `{pin.schema_url}`\n"
        "- **Authority boundary:** This snapshot reports provider-owned software facts. "
        "Its inclusion does not grant scientific qualification, human validation, coaching "
        "authority, or engineering approval.\n"
        ":::\n"
    ).encode()


def _lock_document(pin: CompanionPin, manifest_size: int, schema_size: int) -> dict[str, object]:
    directory = f"snapshots/{pin.commit}"
    return {
        "schema_version": LOCK_VERSION,
        "provider": {
            "host": pin.provider_host,
            "repository": pin.provider_repository,
            "commit": pin.commit,
            "revision_url": f"{PROVIDER_REPOSITORY_URL}/tree/{pin.commit}",
            "manifest_acquisition": pin.acquisition,
            "manifest_provider_path": pin.manifest_provider_path,
            "generator_command": pin.generator_command,
            "manifest_url": pin.manifest_url,
            "schema_url": pin.schema_url,
            "manifest_sha256": pin.manifest_sha256,
            "schema_sha256": pin.schema_sha256,
            "manifest_bytes": manifest_size,
            "schema_bytes": schema_size,
            "provider_schema_id": PROVIDER_SCHEMA_ID,
        },
        "snapshot": {
            "directory": directory,
            "manifest_path": f"{directory}/{MANIFEST_NAME}",
            "schema_path": f"{directory}/{PROVIDER_SCHEMA_NAME}",
            "provenance_path": f"{directory}/{PROVENANCE_NAME}",
        },
        "publication": {
            "state": "draft",
            "boundary": (
                "Software-fact provenance only; scientific qualification, human validation, "
                "coaching authority, and engineering approval remain separate."
            ),
        },
    }


def _canonical_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def _safe_relative(root: Path, relative: str) -> Path:
    path = PurePosixPath(relative)
    if path.is_absolute() or any(part in {".", ".."} for part in path.parts):
        raise CompanionImportError(f"lock path is not normalized: {relative}")
    resolved_root = root.resolve()
    candidate = resolved_root.joinpath(*path.parts).resolve()
    try:
        candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise CompanionImportError(f"lock path escapes snapshot root: {relative}") from exc
    return candidate


def _write_bytes(path: Path, payload: bytes) -> None:
    path.write_bytes(payload)


def _read_bounded_file(path: Path, max_bytes: int, label: str) -> bytes:
    try:
        with path.open("rb") as stream:
            payload = stream.read(max_bytes + 1)
    except OSError as exc:
        raise CompanionImportError(f"cannot read {label}: {exc}") from exc
    if len(payload) > max_bytes:
        raise CompanionImportError(f"{label} exceeds {max_bytes} bytes")
    return payload


class CompanionConsumer:
    """Validate, install, verify, and compare immutable companion snapshots."""

    def __init__(
        self,
        root: Path,
        lock_schema_path: Path,
        *,
        replace: Callable[[Path, Path], None] = os.replace,
        write_bytes: Callable[[Path, bytes], None] = _write_bytes,
    ) -> None:
        self._root = root
        self._lock_schema_path = lock_schema_path
        self._replace = replace
        self._write_bytes = write_bytes

    @property
    def lock_path(self) -> Path:
        """Return the single active-lock path."""
        return self._root / "lock.json"

    def install_from_urls(self, pin: CompanionPin, fetcher: Fetcher) -> InstalledCompanion:
        """Fetch bounded bytes, reject redirect escape, then install atomically."""
        _validate_pin(pin)
        if pin.acquisition != IMMUTABLE_URL or pin.manifest_url is None:
            raise CompanionImportError("URL install requires immutable-url acquisition")
        manifest = fetcher.fetch(pin.manifest_url, MAX_MANIFEST_BYTES)
        _pin_url(pin, manifest.final_url, "manifest", redirected=True)
        schema = fetcher.fetch(pin.schema_url, MAX_SCHEMA_BYTES)
        _pin_url(pin, schema.final_url, "schema", redirected=True)
        return self.install(pin, manifest.data, schema.data)

    def install_from_local_export(
        self, pin: CompanionPin, manifest_path: Path, schema_path: Path
    ) -> InstalledCompanion:
        """Install a reviewed provider export and committed schema from local paths."""
        _validate_pin(pin)
        if pin.acquisition != LOCAL_EXPORT or pin.manifest_url is not None:
            raise CompanionImportError("local install requires protected-local-export acquisition")
        manifest = _read_bounded_file(manifest_path, MAX_MANIFEST_BYTES, "manifest")
        schema = _read_bounded_file(schema_path, MAX_SCHEMA_BYTES, "provider schema")
        return self.install(pin, manifest, schema)

    def _snapshot_payloads(
        self, pin: CompanionPin, manifest: bytes, schema: bytes
    ) -> dict[str, bytes]:
        return {
            MANIFEST_NAME: manifest,
            PROVIDER_SCHEMA_NAME: schema,
            PROVENANCE_NAME: _provenance(pin),
        }

    @staticmethod
    def _verify_existing_snapshot(snapshot: Path, expected: Mapping[str, bytes]) -> None:
        actual_files = {path.name for path in snapshot.iterdir() if path.is_file()}
        if actual_files != set(expected):
            raise CompanionImportError("existing immutable snapshot conflicts with reviewed bytes")
        for name, payload in expected.items():
            if (snapshot / name).read_bytes() != payload:
                raise CompanionImportError(
                    "existing immutable snapshot conflicts with reviewed bytes"
                )

    def _write_staged_snapshot(self, expected: Mapping[str, bytes], snapshots: Path) -> Path:
        stage = Path(tempfile.mkdtemp(prefix=".companion-stage-", dir=snapshots))
        try:
            for name, payload in expected.items():
                self._write_bytes(stage / name, payload)
        except OSError:
            shutil.rmtree(stage)
            raise
        return stage

    def install(
        self, pin: CompanionPin, manifest_bytes: bytes, schema_bytes: bytes
    ) -> InstalledCompanion:
        """Validate fully, then atomically activate immutable bytes.

        Preconditions:
            ``pin`` is reviewer-supplied and all candidate bytes are bounded.
        Postconditions:
            The active lock either points to a completely validated immutable
            snapshot or remains byte-for-byte unchanged after any failure.
        """
        _validate_payloads(pin, manifest_bytes, schema_bytes)
        if self.lock_path.exists():
            self.verify_active()
        expected = self._snapshot_payloads(pin, manifest_bytes, schema_bytes)
        lock = _lock_document(pin, len(manifest_bytes), len(schema_bytes))
        validate_lock(lock, self._lock_schema_path)
        lock_bytes = _canonical_json(lock)
        snapshots = self._root / "snapshots"
        snapshot = snapshots / pin.commit
        stage: Path | None = None
        staged_lock: Path | None = None
        created_snapshot = False
        try:
            snapshots.mkdir(parents=True, exist_ok=True)
            if snapshot.exists():
                self._verify_existing_snapshot(snapshot, expected)
            else:
                stage = self._write_staged_snapshot(expected, snapshots)
                self._replace(stage, snapshot)
                stage = None
                created_snapshot = True
            handle, raw_lock = tempfile.mkstemp(prefix=".companion-lock-", dir=self._root)
            os.close(handle)
            staged_lock = Path(raw_lock)
            staged_lock.write_bytes(lock_bytes)
            self._replace(staged_lock, self.lock_path)
            staged_lock = None
        except (OSError, CompanionImportError) as exc:
            if stage is not None and stage.exists():
                shutil.rmtree(stage)
            if staged_lock is not None and staged_lock.exists():
                staged_lock.unlink()
            if created_snapshot and snapshot.exists():
                shutil.rmtree(snapshot)
            if isinstance(exc, CompanionImportError):
                raise
            raise CompanionImportError(f"atomic install failed: {exc}") from exc
        return self.verify_active()

    def _load_lock(self) -> dict[str, object]:
        try:
            lock = json.loads(self.lock_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise CompanionImportError(f"active lock is unavailable: {exc}") from exc
        return validate_lock(lock, self._lock_schema_path)

    def verify_active(self) -> InstalledCompanion:
        """Verify the active lock, immutable bytes, and embedded provider identity."""
        lock = self._load_lock()
        provider = lock["provider"]
        snapshot_record = lock["snapshot"]
        if not isinstance(provider, dict) or not isinstance(snapshot_record, dict):
            raise CompanionImportError("active lock sections are invalid")
        pin = CompanionPin(
            provider_host=str(provider["host"]),
            provider_repository=str(provider["repository"]),
            commit=str(provider["commit"]),
            manifest_sha256=str(provider["manifest_sha256"]),
            schema_sha256=str(provider["schema_sha256"]),
            acquisition=str(provider["manifest_acquisition"]),
            manifest_provider_path=str(provider["manifest_provider_path"]),
            generator_command=str(provider["generator_command"]),
            manifest_url=(
                str(provider["manifest_url"]) if provider["manifest_url"] is not None else None
            ),
            schema_url=str(provider["schema_url"]),
        )
        manifest_path = _safe_relative(self._root, str(snapshot_record["manifest_path"]))
        schema_path = _safe_relative(self._root, str(snapshot_record["schema_path"]))
        provenance_path = _safe_relative(self._root, str(snapshot_record["provenance_path"]))
        directory_path = _safe_relative(self._root, str(snapshot_record["directory"]))
        if not (
            manifest_path.parent == schema_path.parent == provenance_path.parent == directory_path
        ):
            raise CompanionImportError("active snapshot paths do not share the locked directory")
        try:
            manifest_bytes = manifest_path.read_bytes()
            schema_bytes = schema_path.read_bytes()
            provenance = provenance_path.read_bytes()
        except OSError as exc:
            raise CompanionImportError(f"active snapshot is incomplete: {exc}") from exc
        if provider["manifest_bytes"] != len(manifest_bytes):
            raise CompanionImportError("active manifest byte count does not match the lock")
        if provider["schema_bytes"] != len(schema_bytes):
            raise CompanionImportError("active schema byte count does not match the lock")
        manifest, _ = _validate_payloads(pin, manifest_bytes, schema_bytes)
        if provenance != _provenance(pin):
            raise CompanionImportError("active provenance view is stale or modified")
        snapshot_dir = manifest_path.parent
        if snapshot_dir.name != pin.commit:
            raise CompanionImportError("active snapshot directory does not match provider commit")
        return InstalledCompanion(pin.commit, snapshot_dir, manifest, lock)

    def check_update(
        self, pin: CompanionPin, manifest_bytes: bytes, schema_bytes: bytes
    ) -> UpdateCheck:
        """Validate a candidate and compare it without writing any file."""
        active = self.verify_active()
        _validate_payloads(pin, manifest_bytes, schema_bytes)
        provider = active.lock["provider"]
        if not isinstance(provider, dict):
            raise CompanionImportError("active provider lock is invalid")
        current_manifest = str(provider["manifest_sha256"])
        current_schema = str(provider["schema_sha256"])
        if active.commit == pin.commit and (
            current_manifest != pin.manifest_sha256 or current_schema != pin.schema_sha256
        ):
            raise CompanionImportError(
                "candidate reuses an immutable commit with different reviewed bytes"
            )
        return UpdateCheck(
            current_commit=active.commit,
            candidate_commit=pin.commit,
            update_available=(
                active.commit != pin.commit
                or current_manifest != pin.manifest_sha256
                or current_schema != pin.schema_sha256
            ),
            manifest_changed=current_manifest != pin.manifest_sha256,
            schema_changed=current_schema != pin.schema_sha256,
        )

    def check_local_export_update(
        self, pin: CompanionPin, manifest_path: Path, schema_path: Path
    ) -> UpdateCheck:
        """Read and validate a local candidate without changing the active pin."""
        _validate_pin(pin)
        if pin.acquisition != LOCAL_EXPORT or pin.manifest_url is not None:
            raise CompanionImportError(
                "local update check requires protected-local-export acquisition"
            )
        manifest = _read_bounded_file(manifest_path, MAX_MANIFEST_BYTES, "manifest")
        schema = _read_bounded_file(schema_path, MAX_SCHEMA_BYTES, "provider schema")
        return self.check_update(pin, manifest, schema)
