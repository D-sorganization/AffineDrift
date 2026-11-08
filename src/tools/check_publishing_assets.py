#!/usr/bin/env python3
"""Verify publishing assets and Git LFS retention contracts (#5543)."""

from __future__ import annotations

import argparse
import hashlib
import logging
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LOGGER = logging.getLogger(__name__)

LFS_POINTER_PREFIX = b"version https://git-lfs.github.com/spec/v1"
PDF_MAGIC_BYTES = b"%PDF-"

CANONICAL_DELIVERABLES: dict[str, dict[str, int | str]] = {
    "articles/The_Physics_of_Golf/main.pdf": {
        "min_size": 1_000_000,
        "sha256": "fd579b122feebf3b9a41d3cb85b6d8f050abacecc9f6a6d6805b05820d547e4d",
    },
    "articles/shot_pattern_analysis/report.pdf": {
        "min_size": 1_000_000,
        "sha256": "fd5506da87f5e619a550fb8cc871a0e8195b6fb98965a99809e3238a0f01508b",
    },
    "articles/Launch_Monitor_Technology_Review/main.pdf": {
        "min_size": 500_000,
        "sha256": "b211129c67c4c733075d8ae1e71b0c743a9cacf613793090b6fb3ae5efad14ab",
    },
    "articles/The_Geometry_of_Motion/Volume_0/main.pdf": {
        "min_size": 1_000_000,
        "sha256": "45ef90cf68778aeaf8a1cc3bc59e28838039c1fdfde800bd096c3955f1018a84",
    },
    "articles/The_Geometry_of_Motion/Volume_I/main.pdf": {
        "min_size": 1_000_000,
        "sha256": "0f30500f3dd91811dcee80a2eb23f10270771430ac5fe1f22fb931dc3c49802c",
    },
}


def verify_gitattributes(repo_root: Path) -> list[str]:
    """Verify that .gitattributes correctly scopes LFS to root-only PDFs."""
    gitattributes_path = repo_root / ".gitattributes"
    if not gitattributes_path.is_file():
        return [f"Missing .gitattributes at {gitattributes_path}"]

    lines = gitattributes_path.read_text(encoding="utf-8").splitlines()
    has_root_lfs = any(line.strip().startswith("/*.pdf") and "filter=lfs" in line for line in lines)
    has_pdf_binary = any(line.strip().startswith("*.pdf binary") for line in lines)

    errors: list[str] = []
    if not has_root_lfs:
        errors.append("Expected '/*.pdf filter=lfs diff=lfs merge=lfs -text' in .gitattributes")
    if not has_pdf_binary:
        errors.append("Expected '*.pdf binary' in .gitattributes")
    return errors


def verify_pdf_asset(path: Path) -> list[str]:
    """Verify that a PDF file is non-empty, hydrated, and has valid magic bytes."""
    if not path.is_file():
        return [f"File not found: {path}"]

    size = path.stat().st_size
    if size == 0:
        return [f"PDF asset is empty (0 bytes): {path}"]

    header = path.read_bytes()[:128]
    if header.startswith(LFS_POINTER_PREFIX):
        return [f"PDF asset is an unhydrated Git LFS pointer: {path}"]

    if not header.startswith(PDF_MAGIC_BYTES):
        return [f"PDF asset has invalid PDF magic bytes: {path}"]

    return []


def verify_canonical_manifest(
    repo_root: Path, manifest: dict[str, dict[str, int | str]] | None = None
) -> list[str]:
    """Verify canonical deliverables against minimum size and optional digest."""
    active_manifest = manifest if manifest is not None else CANONICAL_DELIVERABLES
    errors: list[str] = []

    for rel_path, spec in active_manifest.items():
        file_path = repo_root / rel_path
        if not file_path.is_file():
            errors.append(f"missing canonical asset: {rel_path}")
            continue

        size = file_path.stat().st_size
        min_size = int(spec.get("min_size", 0))
        if size < min_size:
            errors.append(f"{rel_path}: {size} bytes is smaller than minimum size {min_size}")

        expected_sha = spec.get("sha256")
        if expected_sha and isinstance(expected_sha, str):
            actual_sha = hashlib.sha256(file_path.read_bytes()).hexdigest()
            if actual_sha != expected_sha:
                errors.append(
                    f"{rel_path}: sha256 mismatch (expected {expected_sha}, got {actual_sha})"
                )

    return errors


def check_all_publishing_assets(repo_root: Path) -> list[str]:
    """Run comprehensive verification across repository publishing assets."""
    errors: list[str] = []
    errors.extend(verify_gitattributes(repo_root))

    target_dirs = [repo_root / "articles", repo_root / "content"]
    for target_dir in target_dirs:
        if not target_dir.is_dir():
            continue
        for pdf_path in sorted(target_dir.rglob("*.pdf")):
            errors.extend(verify_pdf_asset(pdf_path))

    errors.extend(verify_canonical_manifest(repo_root))
    return errors


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for publishing asset verification."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Path to repository root (defaults to repository root)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run verification and exit 1 on errors",
    )
    args = parser.parse_args(argv)

    errors = check_all_publishing_assets(args.repo_root)
    if errors:
        for err in errors:
            sys.stderr.write(f"ERROR: {err}\n")
        return 1

    LOGGER.info("Publishing assets verified successfully.")
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    sys.exit(main())
