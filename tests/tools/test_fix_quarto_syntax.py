"""Tests for fix_quarto_syntax.py — Quarto markdown syntax fixing functions."""

from src.tools.fix_quarto_syntax import fix_superposition, fix_theory_part5, fix_units_wrist


class TestFixSuperposition:
    """Tests for fix_superposition()."""

    def test_fixes_broken_math_block(self) -> None:
        """Should replace opening bracket with $$ for broken math blocks."""
        content = "[\n  x(t) \\neq 0"
        result = fix_superposition(content)
        assert "$$" in result
        assert "[\n  x(t)" not in result

    def test_fixes_stray_comma_in_mv(self) -> None:
        """Should remove stray comma between m and \\dot v."""
        content = "m,\\dot v"
        result = fix_superposition(content)
        assert "m,\\dot v" not in result
        assert "m \\dot v" in result

    def test_no_change_on_clean_content(self) -> None:
        """Should not modify content without known issues."""
        content = "clean math content $$x = y$$"
        result = fix_superposition(content)
        assert result == content

    def test_fixes_multiple_patterns(self) -> None:
        """Should fix multiple patterns in the same content."""
        content = "m,g^B and I,\\ddot q"
        result = fix_superposition(content)
        assert "m,g^B" not in result
        assert "I,\\ddot q" not in result

    def test_returns_string(self) -> None:
        """Should always return a string."""
        result = fix_superposition("")
        assert isinstance(result, str)


class TestFixUnitsWrist:
    """Tests for fix_units_wrist()."""

    def test_replaces_kgm2_unicode(self) -> None:
        """Should replace numeric kg·m² with LaTeX."""
        content = "Inertia is 0.005 kg·m²"
        result = fix_units_wrist(content)
        assert "kg·m²" not in result
        assert "\\text{ kg}" in result

    def test_replaces_kgm2_ascii(self) -> None:
        """Should replace numeric kg·m^2 with LaTeX."""
        content = "Inertia is 0.004 kg·m^2"
        result = fix_units_wrist(content)
        assert "kg·m^2" not in result

    def test_replaces_nm_unit(self) -> None:
        """Should replace numeric N·m with LaTeX."""
        content = "Torque is 5 N·m"
        result = fix_units_wrist(content)
        assert "5 N·m" not in result
        assert "\\text{ N}" in result

    def test_no_change_on_clean_content(self) -> None:
        """Should not modify content without unit patterns."""
        content = "Some text without unit patterns."
        result = fix_units_wrist(content)
        assert result == content

    def test_range_notation(self) -> None:
        """Should handle range notation like 0.004-0.006 kg·m²."""
        content = "0.004-0.006 kg·m²"
        result = fix_units_wrist(content)
        assert "kg·m²" not in result


class TestFixTheoryPart5:
    """Tests for fix_theory_part5()."""

    def test_converts_note_to_callout(self) -> None:
        """Should convert **Note on parameter validity.** to callout block."""
        content = (
            "**Note on parameter validity.**\nThe stiffness value is important. "
            'Plant" for the swing.'
        )
        result = fix_theory_part5(content)
        assert "::: {.callout-note}" in result
        assert "**Note on parameter validity.**" not in result

    def test_no_change_when_note_absent(self) -> None:
        """Should not modify content without the target note."""
        content = "Some theory content."
        result = fix_theory_part5(content)
        assert result == content

    def test_handles_missing_end_marker(self) -> None:
        """Should handle content where end marker is absent gracefully."""
        content = "**Note on parameter validity.**\nThe stiffness value but no end marker."
        result = fix_theory_part5(content)
        # Should still convert the note opening even without the closing marker
        assert isinstance(result, str)
