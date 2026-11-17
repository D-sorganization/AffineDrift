"""Unit tests for publishing assets and Git LFS retention verification (#5543)."""

from __future__ import annotations

from pathlib import Path

from src.tools.check_publishing_assets import (
    check_all_publishing_assets,
    main,
    verify_canonical_manifest,
    verify_gitattributes,
    verify_pdf_asset,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_verify_gitattributes_passes_on_current_repository() -> None:
    """The repository .gitattributes must define root-only LFS and binary *.pdf rules."""
    errors = verify_gitattributes(REPO_ROOT)
    assert not errors, f"Unexpected .gitattributes errors: {errors}"


def test_verify_gitattributes_fails_when_rule_missing(tmp_path: Path) -> None:
    """Missing root LFS rule or binary *.pdf rule must be detected."""
    gitattributes = tmp_path / ".gitattributes"
    gitattributes.write_text("*.pdf binary\n", encoding="utf-8")
    errors = verify_gitattributes(tmp_path)
    assert any("/*.pdf filter=lfs" in err for err in errors)


def test_verify_pdf_asset_detects_unhydrated_lfs_pointer(tmp_path: Path) -> None:
    """Files formatted as Git LFS text pointer stubs must be flagged."""
    pointer_file = tmp_path / "sample.pdf"
    pointer_content = (
        b"version https://git-lfs.github.com/spec/v1\n"
        b"oid sha256:11223344556677889900aabbccddeeff11223344556677889900aabbccddeeff\n"
        b"size 123456\n"
    )
    pointer_file.write_bytes(pointer_content)
    errors = verify_pdf_asset(pointer_file)
    assert any("unhydrated Git LFS pointer" in err for err in errors)


def test_verify_pdf_asset_detects_empty_file(tmp_path: Path) -> None:
    """Zero-byte PDF assets must be flagged."""
    empty_file = tmp_path / "empty.pdf"
    empty_file.write_bytes(b"")
    errors = verify_pdf_asset(empty_file)
    assert any("empty (0 bytes)" in err for err in errors)


def test_verify_pdf_asset_detects_invalid_magic_bytes(tmp_path: Path) -> None:
    """Non-PDF binary files must fail header verification."""
    corrupt_file = tmp_path / "corrupt.pdf"
    corrupt_file.write_bytes(b"NOT A VALID PDF HEADER")
    errors = verify_pdf_asset(corrupt_file)
    assert any("invalid PDF magic bytes" in err for err in errors)


def test_verify_pdf_asset_accepts_valid_pdf(tmp_path: Path) -> None:
    """Valid PDF payloads starting with standard magic bytes must pass."""
    valid_file = tmp_path / "valid.pdf"
    valid_file.write_bytes(b"%PDF-1.7\n%stream\ncontent\n%%EOF")
    errors = verify_pdf_asset(valid_file)
    assert not errors


def test_verify_canonical_manifest_detects_missing_file(tmp_path: Path) -> None:
    """Missing canonical publication deliverables must be flagged."""
    manifest = {
        "articles/The_Physics_of_Golf/main.pdf": {"min_size": 1000},
    }
    errors = verify_canonical_manifest(tmp_path, manifest=manifest)
    assert any("missing canonical asset" in err for err in errors)


def test_verify_canonical_manifest_detects_truncated_file(tmp_path: Path) -> None:
    """Assets smaller than minimum byte threshold must be flagged."""
    target = tmp_path / "articles" / "The_Physics_of_Golf" / "main.pdf"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"%PDF-1.7 stub")
    manifest = {
        "articles/The_Physics_of_Golf/main.pdf": {"min_size": 1000},
    }
    errors = verify_canonical_manifest(tmp_path, manifest=manifest)
    assert any("smaller than minimum size" in err for err in errors)


def test_check_all_publishing_assets_on_repo() -> None:
    """Existing publication assets in repo must satisfy all retention requirements."""
    errors = check_all_publishing_assets(REPO_ROOT)
    assert not errors, f"Repository assets failed check: {errors}"


def test_main_cli_success() -> None:
    """CLI exit code must be 0 for healthy repo check."""
    exit_code = main(["--check", "--repo-root", str(REPO_ROOT)])
    assert exit_code == 0
