"""Post-census routes can reopen under the existing applied-article audit."""

from scripts.claim_audit_ids import (
    APPLIED_ARTICLE_ROUTES,
    DEFERRED_AUDIT_SCOPE_COUNTS,
    deferred_issue_url,
)


def test_later_atlas_route_can_reopen_without_rewriting_original_census() -> None:
    route = "/articles/proximal-distal-falsification-atlas.html"
    assert deferred_issue_url(route) == "https://github.com/D-sorganization/AffineDrift/issues/4059"
    assert route not in APPLIED_ARTICLE_ROUTES
    assert sum(DEFERRED_AUDIT_SCOPE_COUNTS.values()) == 229
