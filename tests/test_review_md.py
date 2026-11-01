"""Root REVIEW.md exists, is allowlisted and cites only real paths (#5289)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from scripts.check_root_hygiene import ALLOWED_TRACKED_ROOT_FILES

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW = REPO_ROOT / "REVIEW.md"
# A backticked token with a slash or a file suffix is treated as a repo path.
PATH = re.compile(r"`([A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+/?|[A-Za-z0-9_.-]+\.(?:md|py|yml|toml))`")


def test_review_md_exists_at_repo_root() -> None:
    assert REVIEW.is_file()


def test_review_md_is_root_allowlisted() -> None:
    assert "REVIEW.md" in ALLOWED_TRACKED_ROOT_FILES


def test_review_md_cites_only_existing_paths() -> None:
    cited = PATH.findall(REVIEW.read_text(encoding="utf-8"))
    assert cited, "REVIEW.md should cite the files its rules point at"
    missing = [p for p in cited if not (REPO_ROOT / p.rstrip("/")).exists()]
    assert missing == []
