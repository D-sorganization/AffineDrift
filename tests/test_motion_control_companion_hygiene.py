"""Guardrails for motion-control companion files (issue #5615)."""

from pathlib import Path

import pytest

from scripts.check_motion_control_companions import (
    REMOVED_COMPANIONS,
    check_motion_control_companions,
)

ROOT = Path(__file__).resolve().parents[1]
MOTION_CONTROL = ROOT / "articles" / "motion-control"

_SCAN_ROOTS = (
    ROOT / "articles",
    ROOT / "tests",
    ROOT / "docs",
    ROOT / "research",
    ROOT / "scripts",
)
_SKIP_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pyc", ".zip"}


def _looks_like_companion_path_reference(name: str, body: str) -> bool:
    """True when body cites the removed file as a repo path, not merely by basename."""
    return any(
        token in body for token in (f"articles/motion-control/{name}", f"motion-control/{name}")
    )


def test_motion_control_companion_check_is_clean() -> None:
    violations = check_motion_control_companions(MOTION_CONTROL)
    assert not violations, "\n".join(violations)


def test_removed_jsx_and_transcript_companions_are_absent() -> None:
    for name in REMOVED_COMPANIONS:
        assert not (MOTION_CONTROL / name).exists(), f"stale companion still present: {name}"


@pytest.mark.parametrize("name", REMOVED_COMPANIONS)
def test_repo_has_no_links_to_removed_motion_control_companions(name: str) -> None:
    matches: list[str] = []
    for base in _SCAN_ROOTS:
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix in _SKIP_SUFFIXES:
                continue
            if path == Path(__file__):
                continue
            try:
                body = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if _looks_like_companion_path_reference(name, body):
                matches.append(str(path.relative_to(ROOT)))
    assert not matches, f"links to removed companion {name}: {matches[:10]}"
