from src.tools.utils import constants


def test_imports():
    assert constants


def test_exclude_dirs():
    assert constants.EXCLUDE_DIRS
    assert ".git" in constants.EXCLUDE_DIRS_PYTHON
    assert "docs" in constants.EXCLUDE_DIRS_CONTENT


# ── Core constants env-var helpers ──────────────────────────────────────────


def test_env_float_returns_default_when_unset():
    """_env_float falls back to default when the env var is absent."""
    from src.core.constants import _env_float

    assert _env_float("__NONEXISTENT_AD_VAR__", 3.14) == 3.14


def test_env_float_reads_value(monkeypatch):
    """_env_float parses a valid float from the environment."""
    from src.core.constants import _env_float

    monkeypatch.setenv("__TEST_AD_FLOAT__", "2.5")
    assert _env_float("__TEST_AD_FLOAT__", 0.0) == 2.5


def test_env_float_ignores_bad_value(monkeypatch):
    """_env_float returns default on non-numeric input."""
    from src.core.constants import _env_float

    monkeypatch.setenv("__TEST_AD_BAD__", "not-a-number")
    assert _env_float("__TEST_AD_BAD__", 7.7) == 7.7


def test_env_int_returns_default_when_unset():
    """_env_int falls back to default when the env var is absent."""
    from src.core.constants import _env_int

    assert _env_int("__NONEXISTENT_AD_INT__", 42) == 42


def test_env_int_reads_value(monkeypatch):
    """_env_int parses a valid integer from the environment."""
    from src.core.constants import _env_int

    monkeypatch.setenv("__TEST_AD_INT__", "99")
    assert _env_int("__TEST_AD_INT__", 0) == 99


def test_env_int_ignores_bad_value(monkeypatch):
    """_env_int returns default on non-integer input."""
    from src.core.constants import _env_int

    monkeypatch.setenv("__TEST_AD_INT_BAD__", "xyz")
    assert _env_int("__TEST_AD_INT_BAD__", 10) == 10
