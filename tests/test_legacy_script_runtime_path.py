"""Regression tests for removing the legacy script.js runtime path."""

from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "relative_path, legacy_snippet",
    [
        (
            "_includes/site-after-body.html",
            "script.js",
        ),
        (
            "_templates/latex_article.html",
            "script.js",
        ),
        (
            "_templates/partials/laymans-terms.html",
            "script.js",
        ),
        (
            "service-worker.js",
            "/script.js",
        ),
        (
            "content/wrist-as-universal-joint/Wrist_Universal_Claude.html",
            "script.js",
        ),
        (
            "content/inverse-dynamics-analysis/Drafts/inverse-dynamics-claude-current/inverse_dynamics_article.html",
            "script.js",
        ),
        # `articles/tangent-hyperplane-articles/Advanced/Contraction_Tangent_Unification.html`
        # was listed here until #3741 removed it. It was a stale Quarto build
        # artifact committed into the source tree, superseded by the `.qmd`
        # beside it, and the site never served it.
    ],
)
def test_runtime_files_do_not_reference_legacy_script(relative_path, legacy_snippet):
    """Runtime-facing files should load the module entry point only."""
    path = Path(relative_path)
    assert path.exists(), (
        f"{relative_path} is listed here but does not exist. If it was deleted "
        f"deliberately, remove its entry; this test fails with a bare "
        f"FileNotFoundError otherwise, which does not say what to do."
    )
    content = path.read_text(encoding="utf-8")
    assert legacy_snippet not in content
    assert "js/main.js" in content
