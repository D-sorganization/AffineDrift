from typing import Optional

from src.tools.utils.validation_utils import BaseValidator


class User(BaseValidator):
    name: str
    age: int


def test_base_validator_success():
    data = {"name": "Alice", "age": 30}
    user = User.validate_data(data)
    assert user is not None
    assert user.name == "Alice"
    assert user.age == 30


def test_base_validator_failure(caplog):
    data = {"name": "Bob", "age": "not an int"}
    user = User.validate_data(data)
    assert user is None
    # We expect an error log
    assert "Validation error" in caplog.text
