"""Tests for controlled maturity vocabulary and front-matter compliance (WEB-04.1 #4515).

Verifies:
1. config/maturity.yml defines all 6 canonical states with label, definition, establishes, and does_not_establish.
2. Legacy status strings are correctly mapped onto canonical states.
3. Unknown/invalid status strings are rejected with ValueError.
4. All QMD front matter and HTML status badges across content directories conform to the vocabulary.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from src.tools.utils.content_utils import collect_qmd_files, read_qmd_with_frontmatter
from src.tools.utils.maturity import (
    CanonicalMaturityState,
    load_maturity_config,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "config" / "maturity.yml"


def test_maturity_config_structure() -> None:
    """Verify config/maturity.yml exists and contains all required semantic fields."""
    assert CONFIG_PATH.is_file(), f"Missing config file: {CONFIG_PATH}"
    vocab = load_maturity_config(CONFIG_PATH)

    expected_enum = {e.value for e in CanonicalMaturityState}
    assert set(vocab.states.keys()) == expected_enum

    for key, defn in vocab.states.items():
        assert defn.key == key
        assert len(defn.label) > 0
        assert len(defn.definition) > 10
        assert len(defn.establishes) > 10
        assert len(defn.does_not_establish) > 10

    assert len(vocab.legacy_mappings) >= 10
    for legacy, target in vocab.legacy_mappings.items():
        assert target in vocab.states, f"Legacy mapping '{legacy}' -> '{target}' is not in states"


@pytest.mark.parametrize(
    "raw_input,expected_canonical",
    [
        ("available", "available"),
        ("Available", "available"),
        ("VALIDATED", "validated"),
        ("experimental", "experimental"),
        ("Planned", "planned"),
        ("Deprecated", "deprecated"),
        ("Opinion", "opinion"),
        ("In Progress (Scaffolding Phase)", "planned"),
        ("EXPLORATORY", "experimental"),
        ("scaffolded", "planned"),
        ("canonical / reference / exploratory", "available"),
        ("Available computational publication", "available"),
        ("Supported / Extended", "available"),
        ("draft", "experimental"),
        ("reviewed", "validated"),
        ("verified", "validated"),
        ("archived", "deprecated"),
    ],
)
def test_maturity_resolution(raw_input: str, expected_canonical: str) -> None:
    """Verify canonical and legacy inputs resolve to their expected canonical state."""
    vocab = load_maturity_config(CONFIG_PATH)
    assert vocab.resolve(raw_input) == expected_canonical


def test_invalid_status_rejected() -> None:
    """Verify unknown or invented status strings raise ValueError."""
    vocab = load_maturity_config(CONFIG_PATH)
    with pytest.raises(ValueError, match="Invalid maturity status"):
        vocab.resolve("invented-status-string")
    with pytest.raises(ValueError, match="Invalid maturity status"):
        vocab.resolve("production-ready")
    with pytest.raises(ValueError, match="Invalid maturity status"):
        vocab.resolve("arbitrary")


def test_all_qmd_frontmatter_status_conforms() -> None:
    """Scan all QMD content pages and verify every declared status/maturity is valid."""
    vocab = load_maturity_config(CONFIG_PATH)
    content_dirs = [
        ".",
        "articles",
        "books",
        "critiques",
        "models",
        "pages",
        "repositories",
        "resources",
    ]

    files_checked = 0
    statuses_found: set[str] = set()

    for qmd_path in collect_qmd_files(content_dirs):
        files_checked += 1
        _content, fm = read_qmd_with_frontmatter(qmd_path)
        status_val = fm.get("status") or fm.get("maturity")
        if status_val:
            status_str = str(status_val).strip()
            # Must resolve without error
            resolved = vocab.resolve(status_str)
            assert resolved in vocab.states
            statuses_found.add(status_str)

    assert files_checked > 20


def test_html_status_badges_conform() -> None:
    """Scan pages with HTML status-badge classes to verify the variant matches canonical states."""
    vocab = load_maturity_config(CONFIG_PATH)
    canonical_keys = vocab.canonical_keys()
    badge_regex = re.compile(r'class="[^"]*status-badge--([a-z0-9-]+)[^"]*"')

    content_dirs = [".", "pages", "resources", "articles"]
    badge_count = 0
    for qmd_path in collect_qmd_files(content_dirs):
        text = qmd_path.read_text(encoding="utf-8", errors="ignore")
        matches = badge_regex.findall(text)
        for variant in matches:
            badge_count += 1
            # Variant must either be a canonical state or a mapped legacy key
            assert (
                variant in canonical_keys or variant in vocab.legacy_mappings
            ), f"Invalid status badge variant '{variant}' in {qmd_path}"

    assert badge_count > 0, "Expected to find at least one status badge in content pages"
