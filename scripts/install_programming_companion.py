"""Install the UpstreamDrift companion bundle as the active programming-companion pin.

UpstreamDrift publishes ``upstreamdrift-companion-<sha>`` as an attested GitHub
Actions artifact (``release.yml``). This CLI takes the extracted bundle
directory (``--source``) or downloads it by name with ``gh`` (``--fetch``),
verifies the sidecar ``.sha256`` digests, runs it through the fail-closed
consumer (schema identity, digests, commit binding, path safety), atomically
installs it under ``data/companion/`` and records an acquisition receipt.

Usage:
    python -m scripts.install_programming_companion --source <dir> --commit <sha>
    python -m scripts.install_programming_companion --fetch upstreamdrift-companion-<sha>
    ... --replace --expected-active-lock-sha256 <digest>   # explicit pin replacement
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.cli_output import write_stderr, write_stdout
from src.affine_control.programming_companion import (
    AcquisitionError,
    CompanionConsumer,
    ConsumerPolicy,
    DirectoryTransport,
    ImportRequest,
    SnapshotStore,
)
from src.affine_control.programming_companion.models import COMMIT_PATTERN

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STORE = ROOT / "data" / "companion"
ACQUISITION_NAME = "acquisition.json"
ACQUISITION_SCHEMA = "affinedrift/upstreamdrift-companion-acquisition/v1"
ARTIFACT_NAME_PATTERN = re.compile(r"^upstreamdrift-companion-([0-9a-f]{40})$")
SIDE_CAR_PATTERN = re.compile(r"^([0-9a-f]{64})\s+(\S+)\s*$")


def read_sidecar_digest(bundle: Path, name: str) -> str:
    """Return the digest declared by ``<name>.sha256`` after checking its target."""
    sidecar = bundle / f"{name}.sha256"
    if not sidecar.is_file():
        raise AcquisitionError(f"bundle is missing the {name}.sha256 sidecar")
    match = SIDE_CAR_PATTERN.match(sidecar.read_text(encoding="utf-8"))
    if match is None or match.group(2) != name:
        raise AcquisitionError(f"{name}.sha256 does not describe {name}")
    return match.group(1)


def build_request(policy: ConsumerPolicy, bundle: Path, commit: str) -> ImportRequest:
    """Build the exact import request from the bundle's sidecar digests."""
    if COMMIT_PATTERN.fullmatch(commit) is None:
        raise AcquisitionError("commit must be an exact 40-hex SHA")
    return ImportRequest(
        source_commit=commit,
        manifest_url=policy.object_url(commit, policy.manifest_path),
        manifest_sha256=read_sidecar_digest(bundle, policy.manifest_path),
        schema_url=policy.object_url(commit, policy.schema_path),
        schema_sha256=read_sidecar_digest(bundle, policy.schema_path),
    )


def acquisition_receipt(
    policy: ConsumerPolicy,
    bundle: Path,
    commit: str,
    *,
    artifact_id: int | None,
    run_id: int | None,
    attestation: str,
    fetched_on: str,
) -> dict[str, object]:
    """Describe where the installed bytes came from (the lock stays canonical)."""
    files = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(bundle.iterdir())
        if path.is_file() and not path.name.endswith(".sha256")
    }
    return {
        "schema_version": ACQUISITION_SCHEMA,
        "artifact_name": f"upstreamdrift-companion-{commit}",
        "provider": {"repository": policy.repository_url, "commit": commit},
        "source_kind": "github-actions-artifact",
        "artifact_id": artifact_id,
        "workflow_run_id": run_id,
        "attestation": attestation,
        "fetched_on": fetched_on,
        "bundle_files_sha256": files,
    }


def fetch_artifact(name: str, destination: Path) -> tuple[int, int]:
    """Download and extract one named artifact with ``gh``; return (artifact_id, run_id)."""
    listing = subprocess.run(
        [
            "gh",
            "api",
            f"repos/D-sorganization/UpstreamDrift/actions/artifacts?name={name}&per_page=5",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    artifacts = [a for a in json.loads(listing.stdout)["artifacts"] if not a["expired"]]
    if not artifacts:
        raise AcquisitionError(f"no unexpired artifact named {name}")
    artifact = artifacts[0]
    archive = destination / "artifact.zip"
    with archive.open("wb") as stream:
        subprocess.run(
            [
                "gh",
                "api",
                f"repos/D-sorganization/UpstreamDrift/actions/artifacts/{artifact['id']}/zip",
            ],
            check=True,
            stdout=stream,
        )
    with zipfile.ZipFile(archive) as bundle:
        for member in bundle.infolist():
            if "/" in member.filename or member.filename.startswith(".."):
                raise AcquisitionError(f"artifact contains a nested path: {member.filename}")
        bundle.extractall(destination)
    archive.unlink()
    return int(artifact["id"]), int(artifact["workflow_run"]["id"])


def verify_attestation(bundle: Path, manifest_name: str) -> str:
    """Return the ``gh attestation verify`` outcome as a short evidence string."""
    try:
        result = subprocess.run(
            [
                "gh",
                "attestation",
                "verify",
                str(bundle / manifest_name),
                "-R",
                "D-sorganization/UpstreamDrift",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return "unverified: gh unavailable"
    if result.returncode == 0:
        return "verified: gh attestation verify (actions/attest-build-provenance)"
    return f"failed: gh attestation verify exit {result.returncode}"


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n", maxsplit=1)[0])
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--source", type=Path, help="extracted artifact directory")
    source.add_argument("--fetch", help="artifact name upstreamdrift-companion-<sha> to download")
    parser.add_argument("--commit", help="exact 40-hex provider commit (required with --source)")
    parser.add_argument("--store", type=Path, default=DEFAULT_STORE)
    parser.add_argument("--replace", action="store_true", help="replace the active pin")
    parser.add_argument("--expected-active-lock-sha256", default=None)
    parser.add_argument("--artifact-id", type=int, default=None)
    parser.add_argument("--run-id", type=int, default=None)
    parser.add_argument("--skip-attestation", action="store_true")
    parser.add_argument("--fetched-on", default=dt.datetime.now(dt.UTC).date().isoformat())
    args = parser.parse_args(argv)
    if args.source is not None and not args.commit:
        parser.error("--commit is required with --source")
    if args.replace and not args.expected_active_lock_sha256:
        parser.error("--replace requires --expected-active-lock-sha256")
    return args


def install(args: argparse.Namespace, bundle: Path, commit: str) -> int:
    """Validate, install (or replace), and write the acquisition receipt."""
    policy = ConsumerPolicy.upstreamdrift_actions_artifact()
    prefix = policy.object_url(commit, policy.manifest_path)[: -len(policy.manifest_path)]
    consumer = CompanionConsumer(
        policy, DirectoryTransport(bundle, prefix), SnapshotStore(args.store)
    )
    request = build_request(policy, bundle, commit)
    attestation = (
        "skipped" if args.skip_attestation else verify_attestation(bundle, policy.manifest_path)
    )
    if attestation.startswith("failed"):
        write_stderr(f"refusing to install: {attestation}")
        return 1
    if args.replace:
        lock = consumer.replace_pin(request, args.expected_active_lock_sha256)
    else:
        lock = consumer.install(request)
    receipt = acquisition_receipt(
        policy,
        bundle,
        commit,
        artifact_id=args.artifact_id,
        run_id=args.run_id,
        attestation=attestation,
        fetched_on=args.fetched_on,
    )
    (args.store / ACQUISITION_NAME).write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    write_stdout(
        f"installed {lock.snapshot_id} ({lock.publication_state}) "
        f"manifest sha256 {lock.manifest_sha256} -> {args.store / 'active-lock.json'}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    args = parse_args(argv)
    try:
        if args.source is not None:
            return install(args, args.source, args.commit)
        match = ARTIFACT_NAME_PATTERN.match(args.fetch)
        if match is None:
            raise AcquisitionError("artifact name must be upstreamdrift-companion-<40-hex sha>")
        commit = match.group(1)
        workdir = Path(tempfile.mkdtemp(prefix="companion-"))
        try:
            args.artifact_id, args.run_id = fetch_artifact(args.fetch, workdir)
            return install(args, workdir, commit)
        finally:
            shutil.rmtree(workdir, ignore_errors=True)
    except AcquisitionError as exc:
        write_stderr(f"companion install failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
