"""Regression checks for Tangent Hyperplane label uniqueness."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TANGENT_DIR = REPO_ROOT / "articles" / "Tangent Hyperplane Articles"

LABEL_PATTERN = re.compile(r"\{#([A-Za-z0-9_:-]+)\}")
REFERENCE_PATTERN = re.compile(r"@([A-Za-z0-9_:-]+)")

LEGACY_LABELS = frozenset(
    {
        "eq-complementarity",
        "eq-dynamics",
        "eq-hybrid-cost",
        "eq-linearized-dynamics",
        "eq-residual-bound",
        "eq-residual-def",
        "eq-robot-dynamics",
        "eq-value-function",
        "eq-zvcf_state",
        "sec-applications",
        "sec-conclusion",
        "sec-implementation",
    },
)


def _iter_tangent_docs() -> list[Path]:
    return sorted(p for p in TANGENT_DIR.rglob("*") if p.suffix in {".qmd", ".md"})


def _collect_labels_and_refs(path: Path) -> tuple[set[str], set[str]]:
    text = path.read_text(encoding="utf-8")
    labels = set(LABEL_PATTERN.findall(text))
    refs = set(REFERENCE_PATTERN.findall(text))
    return labels, refs


def test_tangent_hyperplane_labels_are_unique() -> None:
    """Tangent Hyperplane labels should be unique across the directory."""
    seen: dict[str, list[Path]] = {}
    for path in _iter_tangent_docs():
        for label in LABEL_PATTERN.findall(path.read_text(encoding="utf-8")):
            seen.setdefault(label, []).append(path.relative_to(REPO_ROOT))

    duplicates = {label: files for label, files in seen.items() if len(files) > 1}
    assert duplicates == {}, f"Duplicate labels remain in Tangent Hyperplane docs: {duplicates}"


def test_tangent_hyperplane_issue_2347_legacy_labels_removed() -> None:
    """Legacy duplicate IDs from issue #2347 should be fully retired in this tree."""
    all_labels: set[str] = set()
    all_refs: set[str] = set()

    for path in _iter_tangent_docs():
        labels, refs = _collect_labels_and_refs(path)
        all_labels.update(labels)
        all_refs.update(refs)

    leaked = sorted(item for item in LEGACY_LABELS if item in all_labels or item in all_refs)
    assert leaked == [], (
        f"Legacy issue #2347 labels still present in Tangent Hyperplane docs: {leaked}"
    )
