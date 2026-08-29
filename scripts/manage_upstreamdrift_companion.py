#!/usr/bin/env python3
"""Install, verify, or compare the immutable UpstreamDrift companion manifest."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from src.companion.manifest_consumer import (
    IMMUTABLE_URL,
    LOCAL_EXPORT,
    MANIFEST_PROVIDER_PATH,
    CompanionConsumer,
    CompanionImportError,
    CompanionPin,
    HttpFetcher,
    InstalledCompanion,
    UpdateCheck,
)

LOGGER = logging.getLogger(__name__)
DEFAULT_ROOT = Path("data/upstreamdrift_companion")
DEFAULT_LOCK_SCHEMA = Path("schemas/upstreamdrift-companion-lock-v1.schema.json")


def _add_pin_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--commit", required=True, help="exact protected 40-hex revision")
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--schema-sha256", required=True)
    parser.add_argument("--schema-url", required=True, help="immutable raw schema URL")
    parser.add_argument(
        "--generator-command",
        required=True,
        help="reviewed provider command that produced the manifest bytes",
    )


def _add_local_arguments(parser: argparse.ArgumentParser) -> None:
    _add_pin_arguments(parser)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)


def build_parser() -> argparse.ArgumentParser:
    """Build the deterministic command-line contract."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--lock-schema", type=Path, default=DEFAULT_LOCK_SCHEMA)
    commands = parser.add_subparsers(dest="command", required=True)

    install_local = commands.add_parser(
        "install-local", help="atomically install reviewed local export bytes"
    )
    _add_local_arguments(install_local)

    install_url = commands.add_parser(
        "install-url", help="download and install an immutable tracked manifest"
    )
    _add_pin_arguments(install_url)
    install_url.add_argument("--manifest-url", required=True)

    check_local = commands.add_parser(
        "check-local", help="validate and compare local export bytes without writing"
    )
    _add_local_arguments(check_local)

    commands.add_parser("verify", help="verify the active lock and every immutable byte")
    return parser


def _pin(args: argparse.Namespace, acquisition: str) -> CompanionPin:
    manifest_url = args.manifest_url if acquisition == IMMUTABLE_URL else None
    return CompanionPin(
        provider_host="github.com",
        provider_repository="D-sorganization/UpstreamDrift",
        commit=args.commit,
        manifest_sha256=args.manifest_sha256,
        schema_sha256=args.schema_sha256,
        acquisition=acquisition,
        manifest_provider_path=MANIFEST_PROVIDER_PATH,
        generator_command=args.generator_command,
        manifest_url=manifest_url,
        schema_url=args.schema_url,
    )


def _installed_result(installed: InstalledCompanion) -> dict[str, object]:
    return {
        "commit": installed.commit,
        "manifest_id": installed.manifest["manifest_id"],
        "snapshot": installed.snapshot_dir.as_posix(),
        "verified": True,
    }


def _update_result(update: UpdateCheck) -> dict[str, object]:
    return {
        "candidate_commit": update.candidate_commit,
        "current_commit": update.current_commit,
        "manifest_changed": update.manifest_changed,
        "schema_changed": update.schema_changed,
        "update_available": update.update_available,
        "wrote_files": False,
    }


def main(argv: list[str] | None = None) -> int:
    """Run one explicit companion operation and emit deterministic JSON."""
    args = build_parser().parse_args(argv)
    consumer = CompanionConsumer(args.root, args.lock_schema)
    try:
        if args.command == "verify":
            result = _installed_result(consumer.verify_active())
        elif args.command == "install-local":
            result = _installed_result(
                consumer.install_from_local_export(
                    _pin(args, LOCAL_EXPORT), args.manifest, args.schema
                )
            )
        elif args.command == "install-url":
            result = _installed_result(
                consumer.install_from_urls(_pin(args, IMMUTABLE_URL), HttpFetcher())
            )
        else:
            result = _update_result(
                consumer.check_local_export_update(
                    _pin(args, LOCAL_EXPORT), args.manifest, args.schema
                )
            )
    except CompanionImportError as exc:
        LOGGER.error("%s", exc)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    raise SystemExit(main())
