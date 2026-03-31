"""Tests for scripts.mypy_models - data models and constants."""

from scripts.mypy_models import (
    COMMON_TYPE_IMPORTS,
    GENERIC_SUPPRESSIBLE,
    IMPORT_SUPPRESSIBLE,
    KNOWN_UNTYPED_MODULES,
    AgentReport,
    Fix,
    MypyError,
)


class TestMypyError:
    def test_creation(self):
        err = MypyError(
            file="src/foo.py",
            line=10,
            column=5,
            severity="error",
            message="Name 'X' is not defined",
            code="name-defined",
        )
        assert err.file == "src/foo.py"
        assert err.line == 10
        assert err.code == "name-defined"

    def test_defaults_are_data(self):
        # Just verifying it's a plain dataclass with no hidden state.
        err1 = MypyError("a.py", 1, 1, "error", "msg", "code")
        err2 = MypyError("a.py", 1, 1, "error", "msg", "code")
        assert err1 == err2


class TestFix:
    def test_default_original_code_empty(self):
        fix = Fix(file="src/a.py", line=5, description="desc", strategy="real-fix")
        assert fix.original_code == ""

    def test_strategy_values(self):
        for strat in ("real-fix", "suppression"):
            fix = Fix(file="x.py", line=1, description="d", strategy=strat)
            assert fix.strategy == strat


class TestAgentReport:
    def test_default_zero_counts(self):
        r = AgentReport()
        assert r.total_errors == 0
        assert r.errors_fixed == 0
        assert r.real_fixes == 0
        assert r.suppressions == 0

    def test_mutable_lists_independent(self):
        r1 = AgentReport()
        r2 = AgentReport()
        r1.files_modified.append("foo.py")
        assert "foo.py" not in r2.files_modified


class TestConstants:
    def test_known_untyped_modules_is_frozenset(self):
        assert isinstance(KNOWN_UNTYPED_MODULES, frozenset)
        assert "scipy" in KNOWN_UNTYPED_MODULES

    def test_common_type_imports_has_callable(self):
        assert "Callable" in COMMON_TYPE_IMPORTS
        assert "from collections.abc" in COMMON_TYPE_IMPORTS["Callable"]

    def test_import_suppressible_subset(self):
        assert "import-untyped" in IMPORT_SUPPRESSIBLE
        assert "import-not-found" in IMPORT_SUPPRESSIBLE

    def test_generic_suppressible_includes_assignment(self):
        assert "assignment" in GENERIC_SUPPRESSIBLE
        assert "arg-type" in GENERIC_SUPPRESSIBLE
