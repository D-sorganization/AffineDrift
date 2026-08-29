"""Contract tests for the public offline fallback page."""

from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def test_offline_page_has_public_shell_semantics() -> None:
    """The fallback remains navigable and verifiable when normal routing fails."""
    document = BeautifulSoup((ROOT / "offline.html").read_text(encoding="utf-8"), "html.parser")

    canonical = document.find("link", rel="canonical")
    assert canonical is not None
    assert canonical.get("href") == "https://affinedrift.com/offline.html"
    assert len(document.select("main h1")) == 1
    assert document.select_one("nav a[href='/']") is not None
    assert "affinedrift-theme" in document.get_text(" ") + "".join(
        script.get_text() for script in document.find_all("script")
    )
