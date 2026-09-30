"""Guards for ``requirements-docker.lock``, the hash-locked Docker install set.

The Dockerfile installs the lock with ``pip install --require-hashes`` on a
Linux image, so the lock must (a) agree with ``requirements.txt`` and (b) never
force a Windows-only distribution onto Linux. A Windows-only pin without a
Windows environment marker makes pip fall back to the sdist and try to build it
(``pywinpty`` needs Rust + the Windows ConPTY API), which breaks the image.
"""

from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "requirements-docker.lock"
REQUIREMENTS = ROOT / "requirements.txt"

# Distributions that publish only Windows wheels (or are Windows-API bindings
# whose sdist cannot build elsewhere). Extend when the resolver pulls in a new one.
KNOWN_WINDOWS_ONLY = frozenset({"pywinpty", "pywin32", "pywin32-ctypes", "winpty", "wmi"})

_WINDOWS_MARKER = re.compile(
    r"""sys_platform\s*==\s*['"]win32['"]"""
    r"""|os_name\s*==\s*['"]nt['"]"""
    r"""|platform_system\s*==\s*['"]Windows['"]"""
)
_PIN = re.compile(r"^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)(?:\[[^\]]*\])?==(?P<version>[^\s;\\]+)")
_REQ_NAME = re.compile(r"^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)(?:\[[^\]]*\])?(?P<spec>[^;#]*)")


def _normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _lock_entries() -> list[tuple[str, str, str]]:
    """Return ``(normalized_name, version, marker)`` for each pinned lock entry."""
    entries = []
    for line in LOCK.read_text(encoding="utf-8").splitlines():
        if not line or line[0] in " #-\t":
            continue
        match = _PIN.match(line)
        assert match, f"unparseable lock line: {line!r}"
        _, _, marker = line.rstrip(" \\").partition(";")
        entries.append((_normalize(match["name"]), match["version"], marker.strip()))
    return entries


def _top_level_requirements() -> dict[str, str | None]:
    """Map normalized requirement name -> exact pin (``None`` when unpinned)."""
    reqs: dict[str, str | None] = {}
    for raw in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        match = _REQ_NAME.match(line)
        assert match, f"unparseable requirement: {raw!r}"
        spec = match["spec"].strip()
        pin = spec[2:].strip() if spec.startswith("==") else None
        reqs[_normalize(match["name"])] = pin
    return reqs


def _unmarked_windows_only(entries, windows_only) -> list[str]:
    return sorted(
        f"{name}=={version}"
        for name, version, marker in entries
        if name in windows_only and not _WINDOWS_MARKER.search(marker)
    )


def test_lock_parser_flags_unmarked_windows_only_pin() -> None:
    entries = [
        ("pywinpty", "3.0.3", ""),
        ("pywin32", "311", "sys_platform == 'win32'"),
        ("numpy", "2.5.3", ""),
    ]
    assert _unmarked_windows_only(entries, KNOWN_WINDOWS_ONLY) == ["pywinpty==3.0.3"]


def test_known_windows_only_lock_entries_carry_windows_marker() -> None:
    offenders = _unmarked_windows_only(_lock_entries(), KNOWN_WINDOWS_ONLY)
    assert not offenders, (
        "Windows-only distributions pinned without a Windows environment marker "
        f"(Linux Docker build would try to compile them): {offenders}"
    )


def test_lock_covers_every_top_level_requirement() -> None:
    locked: dict[str, set[str]] = {}
    for name, version, _ in _lock_entries():
        locked.setdefault(name, set()).add(version)

    missing = sorted(set(_top_level_requirements()) - set(locked))
    assert not missing, f"requirements.txt entries absent from requirements-docker.lock: {missing}"

    stale = sorted(
        f"{name}: requirements.txt=={pin}, lock=={'/'.join(sorted(locked[name]))}"
        for name, pin in _top_level_requirements().items()
        if pin is not None and pin not in locked[name]
    )
    assert not stale, f"requirements-docker.lock is stale vs requirements.txt: {stale}"


def _has_only_windows_wheels(name: str, version: str) -> bool:
    url = f"https://pypi.org/pypi/{name}/{version}/json"
    with urllib.request.urlopen(url, timeout=30) as response:  # noqa: S310 reason: fixed PyPI host
        files = json.load(response)["urls"]
    wheels = [f["filename"] for f in files if f["filename"].endswith(".whl")]
    return bool(wheels) and all(re.search(r"-win(32|_amd64|_arm64)\.whl$", w) for w in wheels)


@pytest.mark.requires_network
def test_every_windows_only_wheel_set_in_lock_carries_windows_marker() -> None:
    """Exhaustive variant of the known-list check: ask PyPI about every unmarked pin."""
    offenders = [
        f"{name}=={version}"
        for name, version, marker in _lock_entries()
        if not _WINDOWS_MARKER.search(marker) and _has_only_windows_wheels(name, version)
    ]
    assert not offenders, f"Windows-only wheels pinned without a Windows marker: {offenders}"
