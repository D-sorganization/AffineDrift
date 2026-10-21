"""Tests for exact, fail-closed Quarto render cache fingerprints."""

from __future__ import annotations

import hashlib
import subprocess
from collections.abc import Callable, Mapping
from pathlib import Path

import pytest

from scripts.quarto_cache_key import (
    CacheKeyError,
    compute_cache_key,
    fingerprint_bytes,
    main,
)

pytestmark = pytest.mark.integration

_RUNNER = Callable[..., subprocess.CompletedProcess[bytes]]
_INDEX_EXCLUSIONS = (
    ":(exclude)tests/**",
    ":(exclude).github/**",
    ":(exclude)docs/development/**",
    ":(exclude)SPEC.md",
    ":(exclude)changes/**",
)
_RENDER_PATHS = (
    "_quarto.yml",
    "books/chapter.qmd",
    "filters/site-filter.lua",
    "includes/fragment with spaces.qmd",
    "css/site.css",
    "data/measurements.csv",
    "config/schema.json",
    "requirements.lock",
    ".quarto-version",
    "scripts/quarto_cache_key.py",
    "docs/SPEC.md",
)


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],  # noqa: S607 -- fixed local test executable
        capture_output=True,
        check=True,
        timeout=10,
    )


def _write_files(repo: Path, files: Mapping[str, bytes]) -> None:
    for relative, content in files.items():
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    _git(repo, "add", "--all")


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """Create an uncommitted local repository for index-level tests."""
    _git(tmp_path, "init", "--quiet", "--initial-branch=main")
    return tmp_path


def test_fingerprint_bytes_matches_filtered_index_serialization(git_repo: Path) -> None:
    _write_files(
        git_repo,
        {
            "chapter.qmd": b"# Chapter\n",
            "SPEC.md": b"repository specification\n",
            "changes/issue-note.md": b"change fragment\n",
            "tests/test_policy.py": b"test\n",
            ".github/workflows/ci.yml": b"workflow\n",
            "docs/development/note.md": b"developer note\n",
        },
    )
    legacy_index = _git(git_repo, "ls-files", "-s", "-z", "--", ".", *_INDEX_EXCLUSIONS)

    assert fingerprint_bytes(legacy_index.stdout) == hashlib.sha256(legacy_index.stdout).hexdigest()


def test_metadata_only_changes_do_not_change_render_cache_key(git_repo: Path) -> None:
    _write_files(
        git_repo,
        {
            "_quarto.yml": b"project:\n  type: website\n",
            "chapter.qmd": b"# Chapter\n",
            "SPEC.md": b"initial specification\n",
            "changes/edit.md": b"initial edit\n",
            "changes/delete.md": b"delete this\n",
            "changes/rename from.md": b"rename this\n",
            "changes/mode.md": b"mode change\n",
            "changes/überblick.md": b"unicode change\n",
        },
    )
    initial_key = compute_cache_key(git_repo)
    assert initial_key.startswith("quarto-render-v3-")
    (git_repo / "SPEC.md").write_bytes(b"edited specification\r\n")
    (git_repo / "changes/edit.md").write_bytes(b"edited change\n")
    (git_repo / "changes/delete.md").unlink()
    (git_repo / "changes/rename from.md").rename(git_repo / "changes/rename to.md")
    (git_repo / "changes/new item.md").write_bytes(b"new change\n")
    (git_repo / "changes/überblick.md").write_bytes(b"updated unicode change\n")
    _git(git_repo, "update-index", "--chmod=+x", "--", "changes/mode.md")
    _git(git_repo, "add", "--all")

    assert compute_cache_key(git_repo) == initial_key


@pytest.mark.parametrize("relative", _RENDER_PATHS)
def test_render_input_edits_invalidate_key(git_repo: Path, relative: str) -> None:
    _write_files(git_repo, {relative: b"before\n"})
    initial_key = compute_cache_key(git_repo)
    (git_repo / relative).write_bytes(b"after\n")
    _git(git_repo, "add", "--all")

    assert compute_cache_key(git_repo) != initial_key


def test_render_file_add_delete_and_mode_changes_invalidate_key(
    git_repo: Path,
) -> None:
    _write_files(git_repo, {"chapter.qmd": b"# Chapter\n"})
    original_key = compute_cache_key(git_repo)
    (git_repo / "new chapter.qmd").write_bytes(b"# New\n")
    _git(git_repo, "add", "--all")
    added_key = compute_cache_key(git_repo)
    assert added_key != original_key

    (git_repo / "new chapter.qmd").unlink()
    _git(git_repo, "add", "--all")
    deleted_key = compute_cache_key(git_repo)
    assert deleted_key == original_key

    _git(git_repo, "update-index", "--chmod=+x", "--", "chapter.qmd")
    assert compute_cache_key(git_repo) != deleted_key


@pytest.mark.parametrize(
    "payload",
    [
        b"",
        b"not an ls-files record\0",
        b"100644 " + b"a" * 40 + b" 1\tchapter.qmd\0",
        b"100644 " + b"z" * 40 + b" 0\tchapter.qmd\0",
        b"100644 " + b"a" * 40 + b" 0\tchapter.qmd\0\0",
        "100644 oid 0\tchapter.qmd\0",
    ],
)
def test_fingerprint_rejects_empty_malformed_and_unmerged_indexes(
    payload: object,
) -> None:
    with pytest.raises(CacheKeyError):
        fingerprint_bytes(payload)  # type: ignore[arg-type]


def test_all_excluded_records_do_not_create_an_empty_fingerprint() -> None:
    payload = b"100644 " + b"a" * 40 + b" 0\ttests/test_only.py\0"

    with pytest.raises(CacheKeyError):
        fingerprint_bytes(payload)


def test_excluded_records_must_still_be_well_formed_stage_zero_entries() -> None:
    malformed = b"100644 " + b"a" * 40 + b" 1\ttests/test_merge.py\0"

    with pytest.raises(CacheKeyError):
        fingerprint_bytes(malformed)


def test_raw_tabs_and_newlines_remain_render_inputs() -> None:
    record = b"100644 " + b"a" * 40 + b" 0\tbooks/chapter\twith\nline.qmd\0"

    assert fingerprint_bytes(record) == hashlib.sha256(record).hexdigest()


def test_git_index_read_uses_bounded_local_arguments(git_repo: Path) -> None:
    _write_files(git_repo, {"chapter.qmd": b"# Chapter\n"})
    call: dict[str, object] = {}
    calls: list[tuple[list[str], dict[str, object]]] = []

    def run(args: list[str], **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        call["args"] = args
        call.update(kwargs)
        calls.append((args, kwargs))
        return subprocess.run(args, **kwargs)  # type: ignore[arg-type]

    compute_cache_key(git_repo, run=run)

    assert call["args"] == ["git", "ls-files", "-s", "-z", "--", "."]
    assert call["cwd"] == git_repo
    assert call["timeout"] == 15
    assert call["capture_output"] is True
    assert call["text"] is False
    assert "shell" not in call
    assert calls[0][0] == ["git", "rev-parse", "--show-prefix"]
    assert calls[0][1]["timeout"] == 15


def test_nested_directory_is_not_accepted_as_repository_root(git_repo: Path) -> None:
    _write_files(git_repo, {"nested/chapter.qmd": b"# Nested\n"})

    with pytest.raises(CacheKeyError):
        compute_cache_key(git_repo / "nested")


def test_cli_hides_provider_error_and_emits_no_key(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    def run(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[bytes]:
        return subprocess.CompletedProcess([], 1, b"", b"private credential-bearing error")

    with pytest.raises(SystemExit) as result:
        main(["--repo-root", str(tmp_path)], run=run)

    captured = capsys.readouterr()
    assert result.value.code == 1
    assert captured.out == ""
    assert "private credential-bearing error" not in captured.err
    assert "complete Quarto cache key" in captured.err


@pytest.mark.parametrize(
    "result",
    [
        subprocess.CompletedProcess([], 1, b"", b"private git error"),
        subprocess.CompletedProcess([], 0, b"", b""),
        subprocess.TimeoutExpired("git", 10),
    ],
)
def test_git_failures_do_not_return_a_cache_key(git_repo: Path, result: object) -> None:
    _write_files(git_repo, {"chapter.qmd": b"# Chapter\n"})

    def run(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[bytes]:
        if isinstance(result, BaseException):
            raise result
        return result  # type: ignore[return-value]

    with pytest.raises(CacheKeyError):
        compute_cache_key(git_repo, run=run)
