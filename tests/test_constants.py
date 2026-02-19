import pytest

from src.core.constants import _env_float, _env_int
from src.tools.utils import constants


def test_imports():
    assert constants


def test_exclude_dirs():
    assert constants.EXCLUDE_DIRS
    assert ".git" in constants.EXCLUDE_DIRS_PYTHON
    assert "docs" in constants.EXCLUDE_DIRS_CONTENT


# ── Core constants env-var helpers ──────────────────────────────────────────


@pytest.mark.parametrize(
    ("env_var", "env_val", "default", "expected"),
    [
        ("__NONEXISTENT_AD_VAR__", None, 3.14, 3.14),
        ("__TEST_AD_FLOAT__", "2.5", 0.0, 2.5),
        ("__TEST_AD_BAD__", "not-a-number", 7.7, 7.7),
    ],
    ids=["unset-default", "valid-value", "bad-value-fallback"],
)
def test_env_float(monkeypatch, env_var, env_val, default, expected):
    """_env_float handles missing, valid, and invalid environment values."""
    if env_val is not None:
        monkeypatch.setenv(env_var, env_val)
    else:
        monkeypatch.delenv(env_var, raising=False)
    assert _env_float(env_var, default) == expected


@pytest.mark.parametrize(
    ("env_var", "env_val", "default", "expected"),
    [
        ("__NONEXISTENT_AD_INT__", None, 42, 42),
        ("__TEST_AD_INT__", "99", 0, 99),
        ("__TEST_AD_INT_BAD__", "xyz", 10, 10),
    ],
    ids=["unset-default", "valid-value", "bad-value-fallback"],
)
def test_env_int(monkeypatch, env_var, env_val, default, expected):
    """_env_int handles missing, valid, and invalid environment values."""
    if env_val is not None:
        monkeypatch.setenv(env_var, env_val)
    else:
        monkeypatch.delenv(env_var, raising=False)
    assert _env_int(env_var, default) == expected
