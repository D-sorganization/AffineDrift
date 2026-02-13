"""Tests for DRY shared-helper adoption check script."""

from scripts import check_dry_adoption


def test_dry_adoption_check_passes_on_current_repo() -> None:
    """Current repository should satisfy required shared-helper usage."""
    assert check_dry_adoption.main() == 0
