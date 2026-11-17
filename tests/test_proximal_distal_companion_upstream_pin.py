"""Contracts for the lay companion UpstreamDrift evidence pin (#5609)."""

from __future__ import annotations

from pathlib import Path

from scripts.check_proximal_distal_companion_upstream_pins import (
    collect_violations,
    companion_sources,
    load_pin,
)

ROOT = Path(__file__).resolve().parents[1]


def test_canonical_pin_is_full_sha() -> None:
    commit = load_pin()
    assert len(commit) == 40
    assert commit.islower()


def test_companion_sources_use_only_the_canonical_pin() -> None:
    commit = load_pin()
    violations = collect_violations(companion_sources(), commit)
    assert violations == [], "\n".join(violations)


def test_floating_main_links_fail_the_gate(tmp_path: Path) -> None:
    sample = tmp_path / "sample.qmd"
    commit = load_pin()
    sample.write_text(
        "see https://github.com/D-sorganization/UpstreamDrift/blob/main/README.md\n",
        encoding="utf-8",
    )
    violations = collect_violations([sample], commit)
    assert any("floating" in item for item in violations)


def test_journey_front_matter_names_the_same_pin() -> None:
    commit = load_pin()
    journey = (ROOT / "articles/proximal-distal-a-journey-through-the-swing.qmd").read_text(
        encoding="utf-8"
    )
    assert commit[:8] in journey
    assert f"/tree/{commit}/" in journey or f"`{commit[:8]}`" in journey
