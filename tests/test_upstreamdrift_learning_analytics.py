"""Scientific interpretation contracts for the pinned learning/analytics reference."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "articles/upstreamdrift-learning-analytics.qmd"
LIMITATIONS = ROOT / "articles/strokes-gained-limitations.qmd"
PIN = "3afe09c1ed0247a459d16bf75cf0b28bb64f584a"


def test_green_terminal_values_exclude_putting() -> None:
    """Relabelled green cells have zero continuation cost, not putting cost."""
    text = PAGE.read_text(encoding="utf-8")
    assert "strokes-to-green" in text
    assert "`green_terminal()`" in text
    assert "putting is not included" in text
    assert "strokes-to-hole-out from each cell" not in text
    assert "reports strokes-to-hole under" not in text
    assert "Green cells are terminal for the putter" not in text


def test_terminal_condition_is_explicit_and_source_linked() -> None:
    """The raw solver and the optional raster transformation have different roles."""
    text = PAGE.read_text(encoding="utf-8")
    base = f"https://github.com/D-sorganization/UpstreamDrift/blob/{PIN}"
    assert f"{base}/src/shared/python/sg_optimizer/strategy.py#L56-L65" in text
    assert f"{base}/src/shared/python/sg_optimizer/mdp/value_iteration.py#L174-L183" in text
    assert "only `holed` cells are terminal" in text
    assert "does not call `green_terminal()` automatically" in text
    assert r"V(s_{\mathrm{green}})=0" in text
    assert r"1+V(s_{\mathrm{green}})=1" in text
    assert "1.8" in text


def test_strokes_gained_limitations_matches_green_terminal_semantics() -> None:
    """The limitations article must not relabel the optimiser as strokes-to-hole-out."""
    text = LIMITATIONS.read_text(encoding="utf-8")
    assert "strokes-to-green" in text
    assert "`green_terminal()`" in text
    assert "strokes-to-hole under that model" not in text
