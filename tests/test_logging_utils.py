import logging

from src.tools.utils import logging_utils


def test_imports():
    assert logging_utils


def test_setup_logging():
    logger = logging_utils.setup_logging("test_logger")
    assert isinstance(logger, logging.Logger)
