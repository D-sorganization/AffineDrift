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
        (
            "articles/Tangent Hyperplane Articles/Advanced/Contraction_Tangent_Unification.html",
            "script.js",
        ),
    ],
)
def test_runtime_files_do_not_reference_legacy_script(relative_path, legacy_snippet):
    """Runtime-facing files should load the module entry point only."""
    content = Path(relative_path).read_text(encoding="utf-8")
    assert legacy_snippet not in content
    assert "js/main.js" in content
