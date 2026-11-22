"""Reject ambiguous state and legacy alias keys at the YAML boundary."""

from pathlib import Path
from typing import Any

import pytest
import yaml

from src.tools.utils.maturity import load_maturity_config

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "maturity.yml"


def _write_config(tmp_path: Path, data: dict[str, Any]) -> Path:
    path = tmp_path / "maturity.yml"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


@pytest.mark.parametrize("section", ["states", "legacy_mappings"])
@pytest.mark.parametrize("key", [None, 1, "", "   "])
def test_invalid_vocabulary_keys_are_rejected(tmp_path: Path, section: str, key: object) -> None:
    """Only nonempty string keys may enter the vocabulary."""
    data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    data[section][key] = data[section][next(iter(data[section]))]
    with pytest.raises(ValueError, match="key"):
        load_maturity_config(_write_config(tmp_path, data))


@pytest.mark.parametrize("section", ["states", "legacy_mappings"])
def test_normalized_key_collision_is_rejected(tmp_path: Path, section: str) -> None:
    """Case/whitespace aliases must not silently overwrite an existing entry."""
    data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    key = next(iter(data[section]))
    data[section][f" {key.upper()} "] = data[section][key]
    with pytest.raises(ValueError, match="Duplicate"):
        load_maturity_config(_write_config(tmp_path, data))


def test_unique_normalized_keys_remain_supported(tmp_path: Path) -> None:
    """Normalization remains valid when each normalized key is unique."""
    data = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    for section in ("states", "legacy_mappings"):
        data[section] = {f" {key.upper()} ": value for key, value in data[section].items()}
    vocabulary = load_maturity_config(_write_config(tmp_path, data))
    assert vocabulary.resolve("available") == "available"
    assert vocabulary.resolve("draft") == "experimental"
