"""Tests for clean_latex_comments.py"""

from src.tools.clean_latex_comments import clean_latex_comments_in_file, remove_latex_comments


def test_remove_latex_comments():
    original = """Some normal text
% A comment here
More text
    % Indented comment
%% A double percent should stay
%================
End text
"""
    result = remove_latex_comments(original)

    # We may have extra newlines based on the regex
    assert "Some normal text" in result
    assert "% A comment here" not in result
    assert "More text" in result
    assert "Indented comment" not in result
    assert "%% A double percent should stay" in result
    assert "%================" not in result


def test_clean_latex_comments_in_file(tmp_path):
    f = tmp_path / "test.qmd"
    f.write_text("Hello\n% comment\nWorld", encoding="utf-8")

    assert clean_latex_comments_in_file(f) is True
    content = f.read_text(encoding="utf-8")
    assert "Hello" in content
    assert "% comment" not in content
    assert "World" in content
