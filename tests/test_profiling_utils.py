import logging
import time

from src.tools.utils.profiling_utils import profile_execution_time


def test_profile_execution_time(caplog):
    # Set logger to capture INFO messages
    caplog.set_level(logging.INFO)

    @profile_execution_time
    def slow_function(duration):
        time.sleep(duration)
        return "done"

    result = slow_function(0.01)

    assert result == "done"
    assert "seconds to execute" in caplog.text
