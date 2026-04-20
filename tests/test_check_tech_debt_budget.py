"""Tests for the technical-debt marker budget check script.

Strings that would be detected as broken-window markers are intentionally
obfuscated using concatenation to avoid false-positive self-detection when
this file is scanned by the budget check.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scripts.check_tech_debt_budget import MARKER_RE, MARKERS, main

# Obfuscated marker names for use in assertions — prevents self-detection.
_TODO = "TO" + "DO"
_FIXME = "FIX" + "ME"
_TRACKED_TASK = "TRACKED" + "_TASK"
_TRACKED_DEFECT = "TRACKED" + "_DEFECT"
_HACK = "HA" + "CK"
_XXX = "X" + "XX"


class TestMarkerConfiguration:
    """Tests for MARKERS tuple configuration."""

    def test_markers_includes_backlog_marker(self) -> None:
        """MARKERS must include the backlog-tracking marker."""
        assert any(m.upper() == _TODO for m in MARKERS)

    def test_markers_includes_repair_marker(self) -> None:
        """MARKERS must include the immediate-repair marker."""
        assert any(m.upper() == _FIXME for m in MARKERS)

    def test_markers_includes_tracked_task(self) -> None:
        """MARKERS must include the governed backlog placeholder."""
        assert any(m.upper() == _TRACKED_TASK for m in MARKERS)

    def test_markers_includes_tracked_defect(self) -> None:
        """MARKERS must include the governed defect placeholder."""
        assert any(m.upper() == _TRACKED_DEFECT for m in MARKERS)

    def test_markers_includes_workaround_marker(self) -> None:
        """MARKERS must include the workaround flag."""
        assert any(m.upper() == _HACK for m in MARKERS)

    def test_markers_includes_attention_marker(self) -> None:
        """MARKERS must include the attention-required flag."""
        assert any(m.upper() == _XXX for m in MARKERS)

    def test_markers_has_at_least_six_entries(self) -> None:
        """MARKERS must cover all six tracked categories."""
        assert len(MARKERS) >= 6


class TestMarkerRegex:
    """Tests for MARKER_RE pattern matching."""

    def test_regex_matches_backlog_marker(self) -> None:
        """Regex matches the backlog-tracking marker at word boundaries."""
        assert MARKER_RE.search(f"# {_TODO}: fix this")

    def test_regex_matches_repair_marker(self) -> None:
        """Regex matches the immediate-repair marker at word boundaries."""
        assert MARKER_RE.search(f"# {_FIXME}: broken")

    def test_regex_matches_tracked_task(self) -> None:
        """Regex matches the governed backlog placeholder."""
        assert MARKER_RE.search(f"# {_TRACKED_TASK}: something")

    def test_regex_matches_workaround_marker(self) -> None:
        """Regex matches the workaround flag."""
        assert MARKER_RE.search(f"# {_HACK}: workaround")

    def test_regex_matches_attention_marker(self) -> None:
        """Regex matches the attention-required flag."""
        assert MARKER_RE.search(f"# {_XXX}: needs attention")

    def test_regex_is_case_insensitive(self) -> None:
        """Regex matches lowercase marker variants."""
        assert MARKER_RE.search(f"# {_TODO.lower()}: lowercase")

    def test_regex_requires_word_boundary(self) -> None:
        """Should not match partial words."""
        assert not MARKER_RE.search("autodoc")
        assert not MARKER_RE.search("fixmental")

    def test_regex_does_not_match_empty_string(self) -> None:
        """Empty string produces no match."""
        assert not MARKER_RE.search("")


class TestBudgetCheckMain:
    """Tests for the main() function."""

    def test_main_passes_on_current_codebase(self) -> None:
        """The current codebase must pass the budget check with zero errors."""
        result = main()
        assert result == 0

    def test_main_fails_when_total_budget_exceeded(self, tmp_path: Path) -> None:
        """main() returns non-zero when the total marker budget is exceeded."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "example.py").write_text(f"# {_TODO}: fix me\n", encoding="utf-8")

        with (
            patch(
                "scripts.check_tech_debt_budget.load_config",
                return_value={
                    "include_roots": ["src"],
                    "exclude_substrings": [],
                    "file_extensions": [".py"],
                    "max_total_markers": 0,
                    "max_per_marker": {_TODO: 0},
                },
            ),
            patch(
                "scripts.check_tech_debt_budget.collect_matching_files",
                return_value=[src_dir / "example.py"],
            ),
        ):
            result = main()

        assert result != 0

    def test_main_passes_when_no_markers_found(self, tmp_path: Path) -> None:
        """main() returns 0 when no markers are found in scanned files."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "clean.py").write_text("x = 1\n", encoding="utf-8")

        with (
            patch(
                "scripts.check_tech_debt_budget.load_config",
                return_value={
                    "include_roots": ["src"],
                    "exclude_substrings": [],
                    "file_extensions": [".py"],
                    "max_total_markers": 0,
                    "max_per_marker": {},
                },
            ),
            patch(
                "scripts.check_tech_debt_budget.collect_matching_files",
                return_value=[src_dir / "clean.py"],
            ),
        ):
            result = main()

        assert result == 0
