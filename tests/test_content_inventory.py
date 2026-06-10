"""Content-inventory hygiene guards (IA cleanup #3222).

Prevents large duplicate media assets from re-accumulating in both
``content/`` and ``static/images/`` (only ``static/images/`` is referenced
by the site). ``legacy-pages/`` is intentionally retained as archived
tombstone stubs and is therefore NOT asserted against here.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ONE_MEGABYTE = 1_000_000


def test_no_large_duplicate_media_in_content_and_static() -> None:
    """A >1 MB asset must not exist under both content/ and static/images/."""
    content_dir = REPO_ROOT / "content"
    static_images_dir = REPO_ROOT / "static" / "images"
    if not content_dir.is_dir() or not static_images_dir.is_dir():
        return

    static_names = {
        path.name
        for path in static_images_dir.rglob("*")
        if path.is_file() and path.stat().st_size > ONE_MEGABYTE
    }
    duplicates = sorted(
        path.relative_to(REPO_ROOT).as_posix()
        for path in content_dir.rglob("*")
        if path.is_file() and path.stat().st_size > ONE_MEGABYTE and path.name in static_names
    )
    assert duplicates == [], f"Large duplicate media also under static/images/: {duplicates}"
