"""Tests for the CLI output helpers (issue #3230)."""

from __future__ import annotations

from scripts.cli_output import write_stderr, write_stdout


def test_write_stdout_appends_newline(capsys):
    write_stdout("hello")
    out = capsys.readouterr().out
    assert out == "hello\n"


def test_write_stdout_empty_writes_bare_newline(capsys):
    write_stdout()
    assert capsys.readouterr().out == "\n"


def test_write_stderr_appends_newline(capsys):
    write_stderr("boom")
    err = capsys.readouterr().err
    assert err == "boom\n"


def test_write_stderr_empty_writes_bare_newline(capsys):
    write_stderr()
    assert capsys.readouterr().err == "\n"
