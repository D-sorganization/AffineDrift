import logging
import sys
from importlib import import_module

from src.tools.utils import logging_utils


def test_imports():
    assert logging_utils


def test_setup_logging():
    logger = logging_utils.setup_logging("test_logger")
    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.INFO


def test_setup_logging_with_timestamp():
    logger = logging_utils.setup_logging_with_timestamp("test_ts_logger")
    assert isinstance(logger, logging.Logger)


# ── Environment variable configuration tests ────────────────────────────────


def test_resolve_log_level_default():
    """Default level is INFO when env var is unset."""
    assert logging_utils._resolve_log_level() == logging.INFO


def test_resolve_log_level_from_env(monkeypatch):
    """LOG_LEVEL env var overrides the default."""
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    assert logging_utils._resolve_log_level() == logging.DEBUG


def test_resolve_log_level_invalid_falls_back(monkeypatch):
    """Invalid LOG_LEVEL falls back to INFO."""
    monkeypatch.setenv("LOG_LEVEL", "NOTALEVEL")
    assert logging_utils._resolve_log_level() == logging.INFO


def test_resolve_log_format_default():
    """Default format when env var is unset."""
    fmt = logging_utils._resolve_log_format()
    assert "%(levelname)s" in fmt


def test_resolve_log_format_from_env(monkeypatch):
    """LOG_FORMAT env var overrides the default."""
    monkeypatch.setenv("LOG_FORMAT", "%(message)s")
    assert logging_utils._resolve_log_format() == "%(message)s"


def test_resolve_log_format_timestamp_default():
    """Default timestamp format when env var is unset."""
    fmt = logging_utils._resolve_log_format_timestamp()
    assert "%(asctime)s" in fmt


def test_resolve_log_format_timestamp_from_env(monkeypatch):
    """LOG_FORMAT_TIMESTAMP env var overrides the default."""
    monkeypatch.setenv("LOG_FORMAT_TIMESTAMP", "[%(asctime)s] %(message)s")
    assert logging_utils._resolve_log_format_timestamp() == "[%(asctime)s] %(message)s"


def test_setup_logging_respects_explicit_level():
    """Explicit level parameter takes precedence over env var."""
    logger = logging_utils.setup_logging("test_explicit_level", level=logging.WARNING)
    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.WARNING


def test_setup_logging_does_not_configure_root_for_named_loggers(monkeypatch):
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def fake_basic_config(*args: object, **kwargs: object) -> None:
        calls.append((args, kwargs))

    monkeypatch.setattr(logging, "basicConfig", fake_basic_config)

    logger = logging_utils.setup_logging("src.tools.check_links")

    assert isinstance(logger, logging.Logger)
    assert calls == []


def test_setup_logging_configures_root_for_main(monkeypatch):
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def fake_basic_config(*args: object, **kwargs: object) -> None:
        calls.append((args, kwargs))

    monkeypatch.setattr(logging, "basicConfig", fake_basic_config)

    logger = logging_utils.setup_logging("__main__", format_string="%(message)s")

    assert isinstance(logger, logging.Logger)
    assert calls == [((), {"level": logging.INFO, "format": "%(message)s"})]


def test_importing_module_does_not_configure_root_logging(monkeypatch):
    calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def fake_basic_config(*args: object, **kwargs: object) -> None:
        calls.append((args, kwargs))

    monkeypatch.setattr(logging, "basicConfig", fake_basic_config)

    sys.modules.pop("src.tools.check_links", None)
    import_module("src.tools.check_links")

    assert calls == []
