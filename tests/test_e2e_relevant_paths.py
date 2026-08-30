"""Contracts for the protected E2E and visual-evidence change detector."""

import pytest

from scripts.e2e_relevant_paths import is_e2e_relevant


@pytest.mark.parametrize(
    "path",
    (
        "css/resources.css",
        "custom.scss",
        "styles.css",
        "articles/proximal-distal-companion.css",
        "articles/proximal-distal-energy-transfer.css",
        "articles/proximal_distal_energy_transfer/monograph.css",
        "scripts/verify-public-site-visual.js",
        "scripts/public-site-evidence.js",
        "scripts/public-site-visual-scenario-plan.js",
        "scripts/public_site_manifest.py",
        "scripts/bundle_css.py",
        "schemas/public-site-screenshot-baseline-v1.schema.json",
        "schemas/public-site-screenshot-evidence-v1.schema.json",
        "reports/scientific-claim-audit.md",
        ".github/workflows/ci-standard.yml",
        ".github/workflows/deploy-website.yml",
    ),
)
def test_visual_contract_changes_always_trigger_e2e(path: str) -> None:
    assert is_e2e_relevant(path)


@pytest.mark.parametrize(
    "path",
    (
        "README.md",
        "AGENT_HANDOFF.md",
        "reports/internal-review.md",
        "tests/test_math_only.py",
    ),
)
def test_non_site_changes_do_not_force_e2e(path: str) -> None:
    assert not is_e2e_relevant(path)
