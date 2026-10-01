"""Regression test for issue #4574: unused sitewide metrics.js preload.

`_includes/site-head.html` used to preload `/js/metrics.js` on every page via
`<link rel="preload">`, but only `resources/bibliography.qmd` loads the
script, which triggers an unused-preload console warning on every other
route.
"""

from pathlib import Path


def test_site_head_does_not_preload_metrics_js() -> None:
    """site-head.html must not preload a script only one page uses."""
    content = Path("_includes/site-head.html").read_text(encoding="utf-8")
    assert "metrics.js" not in content


def test_bibliography_still_loads_metrics_js_directly() -> None:
    """The one page that needs metrics.js must still load it."""
    content = Path("resources/bibliography.qmd").read_text(encoding="utf-8")
    assert '<script src="../js/metrics.js"></script>' in content
