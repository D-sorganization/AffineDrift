"""Tests for the reader-prose governance-vocabulary gate (issue #4588).

Reader-facing pages borrowed internal governance jargon -- "governed",
"qualified", "provenance", "protected", "fail-closed" -- from the repository's
own falsification/audit apparatus. The gate flags new occurrences outside the
evidence and developer surfaces (`articles/_generated/`, `models/programming/`)
so the vocabulary does not keep accumulating in prose readers see.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.check_governance_vocabulary import TERMS, key, main, scan

pytestmark = pytest.mark.content_lint


def write(root: Path, relative: str, body: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


class TestScan:
    @pytest.mark.parametrize(
        "body",
        [
            "This finding remains governed until adjudication changes its status.\n",
            "The bundle is a qualified local release candidate.\n",
            "The repository name identifies provenance only.\n",
            "The snapshot is pinned to a protected commit.\n",
            "Validation fails closed on artifact drift.\n",
            "The intake controls are fail-closed by design.\n",
        ],
    )
    def test_flags_each_term_on_a_reader_page(self, tmp_path: Path, body: str) -> None:
        write(tmp_path, "pages/overview.qmd", body)
        assert scan(tmp_path) != []

    def test_ignores_generated_trust_annotations(self, tmp_path: Path) -> None:
        write(
            tmp_path,
            "articles/_generated/trust/critique-annotations/foo.qmd",
            "This claim remains governed pending adjudication.\n",
        )
        assert scan(tmp_path) == []

    def test_ignores_programming_companion_docs(self, tmp_path: Path) -> None:
        write(
            tmp_path,
            "models/programming/provenance.qmd",
            "Manifest provenance is pinned and protected.\n",
        )
        assert scan(tmp_path) == []

    def test_ignores_non_reader_directories(self, tmp_path: Path) -> None:
        write(tmp_path, "critiques/ledger.qmd", "This claim is governed and qualified.\n")
        write(tmp_path, "reports/audit.qmd", "Provenance is protected and fail-closed.\n")
        write(tmp_path, "src/tools/utils/helper.py", "# governed qualified provenance\n")
        assert scan(tmp_path) == []

    def test_ignores_non_qmd_suffixes(self, tmp_path: Path) -> None:
        write(tmp_path, "pages/notes.md", "This is governed and qualified.\n")
        assert scan(tmp_path) == []

    def test_scans_every_configured_reader_root(self, tmp_path: Path) -> None:
        for root in ("articles", "books", "models", "pages", "resources"):
            write(tmp_path, f"{root}/page.qmd", "This is governed.\n")
        found_roots = {Path(f["file"]).parts[0] for f in scan(tmp_path)}
        assert found_roots == {"articles", "books", "models", "pages", "resources"}

    def test_reports_every_occurrence_with_line_numbers(self, tmp_path: Path) -> None:
        write(
            tmp_path,
            "pages/overview.qmd",
            "governed\nfiller\nqualified\n",
        )
        assert sorted(f["line"] for f in scan(tmp_path)) == [1, 3]

    def test_word_boundaries_avoid_false_positives(self, tmp_path: Path) -> None:
        write(
            tmp_path,
            "pages/overview.qmd",
            "The governess praised the unqualified, disqualified entrant.\n",
        )
        assert scan(tmp_path) == []

    def test_fail_closed_matches_hyphen_and_space_forms(self, tmp_path: Path) -> None:
        write(tmp_path, "pages/a.qmd", "fail-closed\n")
        write(tmp_path, "pages/b.qmd", "fails closed\n")
        assert len(scan(tmp_path)) == 2

    def test_every_term_has_a_compiled_pattern(self) -> None:
        assert {label for _, label in TERMS} == {
            "governed",
            "qualified",
            "provenance",
            "protected",
            "fail-closed",
        }


class TestBaseline:
    def test_key_excludes_the_line_number(self, tmp_path: Path) -> None:
        write(tmp_path, "pages/overview.qmd", "governed\n")
        first = key(scan(tmp_path)[0])
        write(tmp_path, "pages/overview.qmd", "padding\npadding\ngoverned\n")
        assert key(scan(tmp_path)[0]) == first

    def test_baselined_occurrence_passes(self, tmp_path: Path) -> None:
        write(tmp_path, "pages/overview.qmd", "governed\n")
        baseline = tmp_path / "baseline.json"
        baseline.write_text(json.dumps([key(scan(tmp_path)[0])]), encoding="utf-8")
        assert main_with(tmp_path, baseline) == 0

    def test_unbaselined_occurrence_fails(self, tmp_path: Path) -> None:
        write(tmp_path, "pages/overview.qmd", "governed\n")
        baseline = tmp_path / "baseline.json"
        baseline.write_text(json.dumps([]), encoding="utf-8")
        assert main_with(tmp_path, baseline) == 1

    def test_baseline_does_not_excuse_a_different_file(self, tmp_path: Path) -> None:
        write(tmp_path, "pages/allowed.qmd", "governed\n")
        baseline = tmp_path / "baseline.json"
        baseline.write_text(json.dumps([key(scan(tmp_path)[0])]), encoding="utf-8")
        write(tmp_path, "pages/other.qmd", "governed\n")
        assert main_with(tmp_path, baseline) == 1


def main_with(root: Path, baseline: Path) -> int:
    """Invoke the CLI entry point against a temporary tree."""
    import sys

    argv = sys.argv
    sys.argv = ["check_governance_vocabulary.py", "--root", str(root), "--baseline", str(baseline)]
    try:
        return main()
    finally:
        sys.argv = argv
