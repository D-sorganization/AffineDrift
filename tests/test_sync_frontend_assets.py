"""Contracts for canonical frontend mirrors used by the deploy artifact."""

from pathlib import Path

from scripts.sync_frontend_assets import SYNC_MAPS

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_every_canonical_javascript_module_has_a_deploy_sync_map() -> None:
    expected = {f"js/{path.name}" for path in (REPO_ROOT / "js").glob("*.js")}
    mapped = {mapping.source for mapping in SYNC_MAPS if mapping.source.startswith("js/")}

    assert mapped == expected
    for mapping in SYNC_MAPS:
        if mapping.source.startswith("js/"):
            assert mapping.mirrors == (f"docs/{mapping.source}",)
