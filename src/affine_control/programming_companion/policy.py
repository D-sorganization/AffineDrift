"""Allowlist policy for immutable UpstreamDrift provider URLs."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlsplit

from .errors import AcquisitionError
from .models import COMMIT_PATTERN, ImportRequest

DEFAULT_MAX_PAYLOAD_BYTES = 5_000_000
RAW_OBJECT_TEMPLATE = "https://{host}/{owner}/{repository_name}/{commit}/{path}"
# UpstreamDrift publishes the companion bundle as the GitHub Actions artifact
# `upstreamdrift-companion-<sha>` (release.yml "Publish exact-commit companion
# artifact", attested with actions/attest-build-provenance). Artifacts are
# addressed by name, not by a raw-object URL, so the lock records this
# name-addressed identity; resolve it with
# `gh api repos/{owner}/{repo}/actions/artifacts?name=<name>` (AffineDrift #4123).
ACTIONS_ARTIFACT_TEMPLATE = (
    "https://{host}/{owner}/{repository_name}/actions/artifacts/"
    "upstreamdrift-companion-{commit}/{path}"
)


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
    url_template: str = RAW_OBJECT_TEMPLATE

    @classmethod
    def upstreamdrift(cls) -> ConsumerPolicy:
        """Return the raw-object UpstreamDrift policy (``dist/companion`` in-tree layout)."""
        return cls(
            host="raw.githubusercontent.com",
            owner="D-sorganization",
            repository_name="UpstreamDrift",
            repository_url="https://github.com/D-sorganization/UpstreamDrift",
            manifest_path="dist/companion/manifest.json",
            schema_path="docs/api/contracts/upstreamdrift-companion-v1.schema.json",
            schema_id=("https://upstreamdrift.dev/schemas/upstreamdrift-companion-v1.schema.json"),
        )

    @classmethod
    def upstreamdrift_actions_artifact(cls) -> ConsumerPolicy:
        """Return the policy for the published ``upstreamdrift-companion-<sha>`` artifact."""
        return cls(
            host="github.com",
            owner="D-sorganization",
            repository_name="UpstreamDrift",
            repository_url="https://github.com/D-sorganization/UpstreamDrift",
            manifest_path="upstreamdrift-companion.v1.json",
            schema_path="upstreamdrift-companion-v1.schema.json",
            schema_id=("https://upstreamdrift.dev/schemas/upstreamdrift-companion-v1.schema.json"),
            url_template=ACTIONS_ARTIFACT_TEMPLATE,
        )

    def object_url(self, commit: str, approved_path: str) -> str:
        """Render the one approved URL for a commit and an approved path."""
        if COMMIT_PATTERN.fullmatch(commit) is None:
            raise AcquisitionError("URL authority requires an exact 40-hex commit")
        if approved_path not in {self.manifest_path, self.schema_path}:
            raise AcquisitionError("only the manifest and schema paths are approved")
        return self.url_template.format(
            host=self.host,
            owner=self.owner,
            repository_name=self.repository_name,
            commit=commit,
            path=approved_path,
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
        if not self.url_template.startswith("https://{host}/") or "{path}" not in self.url_template:
            raise AcquisitionError("URL template must be an https template ending in the path")

    def validate_request(self, request: ImportRequest) -> None:
        """Require exact-commit URLs for the two approved provider paths."""
        self.validate()
        request.validate_digests()
        self.validate_url(request.manifest_url, request.source_commit, self.manifest_path)
        self.validate_url(request.schema_url, request.source_commit, self.schema_path)

    def validate_url(self, url: str, commit: str, approved_path: str) -> None:
        """Reject any URL outside one exact provider object address."""
        if COMMIT_PATTERN.fullmatch(commit) is None:
            raise AcquisitionError("URL authority requires an exact 40-hex commit")
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.hostname != self.host:
            raise AcquisitionError("URL is outside the allowlisted host")
        if parsed.username or parsed.password or parsed.port or parsed.query or parsed.fragment:
            raise AcquisitionError("URL credentials, ports, queries, and fragments are forbidden")
        expected = self.object_url(commit, approved_path)
        if url != expected or "%" in parsed.path or "\\" in parsed.path:
            raise AcquisitionError("URL must use the approved path and exact 40-hex commit")
