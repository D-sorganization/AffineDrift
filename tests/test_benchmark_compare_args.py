"""Tests for the benchmark baseline decision helper (#4913)."""

from __future__ import annotations

import platform
import struct
from pathlib import Path

import pytest

from scripts.ci.benchmark_compare_args import (
    decide,
    format_status,
    machine_id,
    main,
)

LINUX = "Linux-CPython-3.12-64bit"


def _seed(root: Path, mid: str, *names: str) -> None:
    d = root / mid
    d.mkdir(parents=True)
    for n in names:
        (d / n).write_text("{}", encoding="utf-8")


def test_machine_id_matches_pytest_benchmark_format() -> None:
    major, minor = platform.python_version_tuple()[:2]
    expected = (
        f"{platform.system()}-{platform.python_implementation()}"
        f"-{major}.{minor}-{8 * struct.calcsize('P')}bit"
    )
    assert machine_id() == expected


def test_no_baseline_for_platform_saves_without_compare(tmp_path: Path) -> None:
    # Only a Windows baseline is committed, as in the real repo.
    _seed(tmp_path, "Windows-CPython-3.14-64bit", "0001_initial.json")
    d = decide(tmp_path, LINUX)
    assert d.mode == "save"
    assert d.args == ["--benchmark-save=initial"]
    assert not any("compare" in a for a in d.args)
    assert d.artifact_name == f"benchmark-baseline-{LINUX}"


def test_missing_benchmarks_dir_saves(tmp_path: Path) -> None:
    assert decide(tmp_path / "absent", LINUX).mode == "save"


def test_empty_platform_dir_saves(tmp_path: Path) -> None:
    (tmp_path / LINUX).mkdir()
    assert decide(tmp_path, LINUX).mode == "save"


def test_matching_baseline_compares_with_15_percent_gate(tmp_path: Path) -> None:
    _seed(tmp_path, LINUX, "0001_initial.json")
    d = decide(tmp_path, LINUX)
    assert d.mode == "compare"
    assert d.args == ["--benchmark-compare=initial", "--benchmark-compare-fail=mean:15%"]


def test_other_named_baseline_does_not_count(tmp_path: Path) -> None:
    _seed(tmp_path, LINUX, "0001_other.json")
    assert decide(tmp_path, LINUX).mode == "save"


@pytest.mark.parametrize("bad", ["", "../etc", "a/b", "Linux CPython", "x;rm"])
def test_invalid_platform_rejected(tmp_path: Path, bad: str) -> None:
    with pytest.raises(ValueError, match="platform"):
        decide(tmp_path, bad)


@pytest.mark.parametrize("bad", ["", "15", "abc%", "-5%", "0%"])
def test_invalid_threshold_rejected(tmp_path: Path, bad: str) -> None:
    with pytest.raises(ValueError, match="threshold"):
        decide(tmp_path, LINUX, threshold=bad)


def test_status_no_baseline_is_not_failure() -> None:
    msg = format_status("save", "success", LINUX, f"benchmark-baseline-{LINUX}")
    assert msg == (
        f"no baseline for {LINUX}; saved one as artifact "
        f"benchmark-baseline-{LINUX}, commit it under .benchmarks/{LINUX}/ "
        "to enable regression gating"
    )
    assert "failed" not in msg.lower()


def test_status_compare_success() -> None:
    msg = format_status("compare", "success", LINUX, "x")
    assert "All benchmarks passed" in msg and "15%" in msg


def test_status_compare_failure_says_failed() -> None:
    assert "failed" in format_status("compare", "failure", LINUX, "x").lower()


def test_status_not_completed() -> None:
    assert "did not complete" in format_status("save", "cancelled", LINUX, "x")


def test_status_rejects_unknown_mode() -> None:
    with pytest.raises(ValueError, match="mode"):
        format_status("bogus", "success", LINUX, "x")


def test_cli_decide_writes_github_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _seed(tmp_path, LINUX, "0001_initial.json")
    out = tmp_path / "gh_output"
    rc = main(["decide", "--root", str(tmp_path), "--platform", LINUX, "--github-output", str(out)])
    assert rc == 0
    text = out.read_text(encoding="utf-8")
    assert "mode=compare\n" in text
    assert f"platform={LINUX}\n" in text
    assert "args=--benchmark-compare=initial --benchmark-compare-fail=mean:15%\n" in text


def test_cli_invalid_input_exits_2(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["decide", "--platform", "../x"]) == 2
    assert "platform" in capsys.readouterr().err


def test_cli_status_prints_message(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(
        ["status", "--mode", "save", "--outcome", "success", "--platform", LINUX, "--artifact", "a"]
    )
    assert rc == 0
    assert "no baseline for" in capsys.readouterr().out
