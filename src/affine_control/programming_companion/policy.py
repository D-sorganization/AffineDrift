"""Allowlist policy for immutable UpstreamDrift provider URLs."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlsplit

from .errors import AcquisitionError
from .models import COMMIT_PATTERN, ImportRequest

DEFAULT_MAX_PAYLOAD_BYTES = 5_000_000


@dataclass(frozen=True)
class ConsumerPolicy:
    """Closed URL and provider boundary for one companion-manifest family."""

    host: str
    owner: str
    repository_name: str
    repository_url: str
    manifest_path: str
    schema_path: str
    schema_id: str
    max_payload_bytes: int = DEFAULT_MAX_PAYLOAD_BYTES

    @classmethod
    def upstreamdrift(cls) -> ConsumerPolicy:
        """Return the sole approved UpstreamDrift companion policy."""
        return cls(
            host="raw.githubusercontent.com",
            owner="D-sorganization",
            repository_name="UpstreamDrift",
            repository_url="https://github.com/D-sorganization/UpstreamDrift",
            manifest_path="dist/companion/manifest.json",
            schema_path="docs/api/contracts/upstreamdrift-companion-v1.schema.json",
            schema_id=("https://upstreamdrift.dev/schemas/upstreamdrift-companion-v1.schema.json"),
        )

    def validate(self) -> None:
        """Validate configured bounds before any network or file operation."""
        if self.max_payload_bytes <= 0:
            raise AcquisitionError("payload byte limit must be positive")
        for path in (self.manifest_path, self.schema_path):
            if not path or path.startswith("/") or ".." in path.split("/"):
                raise AcquisitionError(
                    "approved repository paths must be relative and traversal-free"
                )

    def validate_request(self, request: ImportRequest) -> None:
        """Require exact-commit URLs for the two approved provider paths."""
        self.validate()
        request.validate_digests()
        self.validate_url(request.manifest_url, request.source_commit, self.manifest_path)
        self.validate_url(request.schema_url, request.source_commit, self.schema_path)

    def validate_url(self, url: str, commit: str, approved_path: str) -> None:
        """Reject any URL outside one exact raw-GitHub object path."""
        if COMMIT_PATTERN.fullmatch(commit) is None:
            raise AcquisitionError("URL authority requires an exact 40-hex commit")
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.hostname != self.host:
            raise AcquisitionError("URL is outside the allowlisted host")
        if parsed.username or parsed.password or parsed.port or parsed.query or parsed.fragment:
            raise AcquisitionError("URL credentials, ports, queries, and fragments are forbidden")
        expected = f"/{self.owner}/{self.repository_name}/{commit}/{approved_path}"
        if parsed.path != expected or "%" in parsed.path or "\\" in parsed.path:
            raise AcquisitionError("URL must use the approved path and exact 40-hex commit")
