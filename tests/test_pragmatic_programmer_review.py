from pathlib import Path

from scripts import pragmatic_programmer_review as ppr


def test_read_text_or_none_logs_warning_for_unreadable_file(
    tmp_path: Path, monkeypatch, caplog
) -> None:
    bad_file = tmp_path / "bad.py"
    bad_file.write_text("print('x')\n", encoding="utf-8")

    original_read_text = Path.read_text

    def fake_read_text(self: Path, *args, **kwargs) -> str:
        if self == bad_file:
            raise OSError("permission denied")
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", fake_read_text)

    with caplog.at_level("WARNING"):
        result = ppr.read_text_or_none(bad_file)

    assert result is None
    assert "Skipping unreadable file" in caplog.text


def test_check_quality_continues_when_file_is_unreadable(tmp_path: Path, monkeypatch) -> None:
    good_file = tmp_path / "good.py"
    bad_file = tmp_path / "bad.py"
    good_file.write_text("# TODO: cleanup\n", encoding="utf-8")
    bad_file.write_text("print('x')\n", encoding="utf-8")

    original_read_text = Path.read_text

    def fake_read_text(self: Path, *args, **kwargs) -> str:
        if self == bad_file:
            raise OSError("permission denied")
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", fake_read_text)

    # No exception should be raised when one file is unreadable.
    issues = ppr.check_quality([good_file, bad_file])
    assert isinstance(issues, list)
