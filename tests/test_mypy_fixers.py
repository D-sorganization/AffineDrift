"""Tests for scripts.mypy_fixers - individual fix strategies."""

from scripts.mypy_fixers import (
    FIX_STRATEGIES,
    add_type_ignore,
    ensure_import,
    fix_callable_as_type,
    fix_generic_suppression,
    fix_import_errors,
    fix_name_not_defined,
    fix_union_attr,
    get_line_indent,
    has_type_ignore,
)
from scripts.mypy_models import MypyError


def _make_error(**kwargs) -> MypyError:
    defaults = dict(file="src/x.py", line=1, column=1, severity="error", message="", code="")
    defaults.update(kwargs)
    return MypyError(**defaults)


class TestGetLineIndent:
    def test_no_indent(self):
        assert get_line_indent("x = 1\n") == ""

    def test_four_spaces(self):
        assert get_line_indent("    x = 1\n") == "    "

    def test_tab(self):
        assert get_line_indent("\tx = 1\n") == "\t"


class TestHasTypeIgnore:
    def test_no_annotation(self):
        assert not has_type_ignore("x = 1\n")

    def test_blanket_ignore(self):
        assert has_type_ignore("x = 1  # type: ignore\n")

    def test_specific_code_present(self):
        assert has_type_ignore("x = 1  # type: ignore[assignment]\n", "assignment")

    def test_specific_code_absent(self):
        assert not has_type_ignore("x = 1  # type: ignore[arg-type]\n", "assignment")

    def test_any_when_code_is_none(self):
        assert has_type_ignore("x = 1  # type: ignore[arg-type]\n", None)


class TestAddTypeIgnore:
    def test_basic_append(self):
        result = add_type_ignore("x = foo()\n", "assignment")
        assert "# type: ignore[assignment]" in result
        assert result.endswith("\n")

    def test_merges_with_existing_bracket(self):
        result = add_type_ignore("x = 1  # type: ignore[arg-type]\n", "assignment")
        assert "arg-type" in result
        assert "assignment" in result

    def test_blanket_ignore_unchanged(self):
        original = "x = 1  # type: ignore\n"
        result = add_type_ignore(original, "assignment")
        # Should not duplicate; blanket ignore is kept
        assert result.endswith("\n")


class TestEnsureImport:
    def test_adds_missing_import(self):
        lines = ["import os\n", "\nx = 1\n"]
        changed = ensure_import(lines, "from typing import Any")
        assert changed
        joined = "".join(lines)
        assert "from typing import Any" in joined

    def test_no_op_when_already_present(self):
        lines = ["from typing import Any\n", "\nx = 1\n"]
        changed = ensure_import(lines, "from typing import Any")
        assert not changed

    def test_inserts_after_last_import(self):
        lines = ["import os\n", "import sys\n", "\n", "x = 1\n"]
        ensure_import(lines, "from pathlib import Path")
        # The new import should appear at index 2 (after sys)
        assert "from pathlib import Path" in lines[2]


class TestFixCallableAsType:
    def test_fixes_lowercase_callable(self):
        lines = ["def foo(cb: callable) -> None:\n", "    pass\n"]
        err = _make_error(line=1, code="valid-type", message='"callable" is not valid as a type')
        fix = fix_callable_as_type(lines, err)
        assert fix is not None
        assert fix.strategy == "real-fix"
        assert "Callable" in lines[0]

    def test_wrong_code_returns_none(self):
        lines = ["def foo(cb: callable) -> None:\n"]
        err = _make_error(line=1, code="arg-type", message='"callable" is not valid as a type')
        assert fix_callable_as_type(lines, err) is None

    def test_no_callable_in_line_returns_none(self):
        lines = ["x = something()\n"]
        err = _make_error(line=1, code="valid-type", message='"callable" is not valid as a type')
        assert fix_callable_as_type(lines, err) is None


class TestFixUnionAttr:
    def test_adds_isinstance_guard(self):
        lines = ["    result = obj.value\n", "    return result\n"]
        err = _make_error(
            line=1,
            code="union-attr",
            message='Item "None" of "MyClass | None" has no attribute "value"',
        )
        fix = fix_union_attr(lines, err)
        assert fix is not None
        assert fix.strategy == "real-fix"
        assert "isinstance" in lines[0]

    def test_wrong_code_returns_none(self):
        lines = ["x.value\n"]
        err = _make_error(
            line=1,
            code="attr-defined",
            message='Item "None" of "A | None" has no attribute "value"',
        )
        assert fix_union_attr(lines, err) is None

    def test_no_match_message_returns_none(self):
        lines = ["x.value\n"]
        err = _make_error(line=1, code="union-attr", message="some other message")
        assert fix_union_attr(lines, err) is None


class TestFixNameNotDefined:
    def test_adds_callable_import(self):
        lines = ["x: Callable = lambda: None\n"]
        err = _make_error(line=1, code="name-defined", message='Name "Callable" is not defined')
        fix = fix_name_not_defined(lines, err)
        assert fix is not None
        assert fix.strategy == "real-fix"
        joined = "".join(lines)
        assert "from collections.abc import Callable" in joined

    def test_unknown_name_returns_none(self):
        lines = ["x: FancyWidget = None\n"]
        err = _make_error(line=1, code="name-defined", message='Name "FancyWidget" is not defined')
        assert fix_name_not_defined(lines, err) is None

    def test_wrong_code_returns_none(self):
        lines = ["x: Callable = None\n"]
        err = _make_error(line=1, code="attr-defined", message='Name "Callable" is not defined')
        assert fix_name_not_defined(lines, err) is None


class TestFixImportErrors:
    def test_suppresses_import_untyped(self):
        lines = ["import scipy\n"]
        err = _make_error(line=1, code="import-untyped", message="Cannot find stubs")
        fix = fix_import_errors(lines, err)
        assert fix is not None
        assert fix.strategy == "suppression"
        assert "type: ignore[import-untyped]" in lines[0]

    def test_wrong_code_returns_none(self):
        lines = ["import scipy\n"]
        err = _make_error(line=1, code="assignment", message="msg")
        assert fix_import_errors(lines, err) is None

    def test_already_suppressed_returns_none(self):
        lines = ["import scipy  # type: ignore[import-untyped]\n"]
        err = _make_error(line=1, code="import-untyped", message="msg")
        assert fix_import_errors(lines, err) is None


class TestFixGenericSuppression:
    def test_suppresses_assignment(self):
        lines = ["x: int = 'hello'\n"]
        err = _make_error(line=1, code="assignment", message="Incompatible types")
        fix = fix_generic_suppression(lines, err)
        assert fix is not None
        assert fix.strategy == "suppression"
        assert "type: ignore[assignment]" in lines[0]

    def test_unknown_code_returns_none(self):
        lines = ["x = 1\n"]
        err = _make_error(line=1, code="unknown-code", message="msg")
        assert fix_generic_suppression(lines, err) is None


class TestFixStrategiesList:
    def test_has_five_strategies(self):
        assert len(FIX_STRATEGIES) == 5

    def test_callable_fix_first(self):
        assert FIX_STRATEGIES[0] is fix_callable_as_type

    def test_generic_suppression_last(self):
        assert FIX_STRATEGIES[-1] is fix_generic_suppression
