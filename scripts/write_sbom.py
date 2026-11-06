"""Write a deterministic CycloneDX 1.5 SBOM from the pinned lockfiles (#5319 slice).

Run as ``python -m scripts.write_sbom``. Inputs are the lockfiles ``write_build_manifest.py`` digests: ``requirements-docker.lock``
(pip, with hashes) and ``package-lock.json`` (npm). The output has no random serial and
takes its timestamp from the commit date, so identical trees give identical bytes.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

from scripts.write_build_manifest import ROOT, _git_head

DEFAULT_OUT = ROOT / "artifacts" / "sbom.cdx.json"
PIP_LOCK = "requirements-docker.lock"
NPM_LOCK = "package-lock.json"
ROOT_COMPONENT_NAME = "affinedrift"
NPM_PREFIX = "node_modules/"
NPM_ALGS = {"sha512": "SHA-512", "sha384": "SHA-384", "sha256": "SHA-256", "sha1": "SHA-1"}

_PIP_PIN = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)(?:\[[^\]]*\])?==([^\s;\\]+)")
_PIP_HASH = re.compile(r"--hash=sha256:([0-9a-fA-F]+)")


class SbomInputError(ValueError):
    """Raised when a lockfile is missing, malformed or lists no packages."""


def _component(
    ecosystem: str, name: str, version: str, hashes: list[dict[str, str]]
) -> dict[str, Any]:
    purl = f"pkg:{ecosystem}/{quote(name, safe='/')}@{version}"
    comp: dict[str, Any] = {
        "type": "library",
        "bom-ref": purl,
        "name": name,
        "version": version,
        "purl": purl,
    }
    if hashes:
        comp["hashes"] = sorted(hashes, key=lambda h: (h["alg"], h["content"]))
    return comp


def _read(repo_root: Path, filename: str) -> str:
    path = repo_root / filename
    if not path.is_file():
        raise SbomInputError(f"{filename}: lockfile not found under {repo_root}")
    return path.read_text(encoding="utf-8")


def parse_pip_lock(text: str) -> list[dict[str, Any]]:
    """Return pypi components from a ``uv pip compile --generate-hashes`` lock."""
    pins: dict[tuple[str, str], list[dict[str, str]]] = {}
    current: list[dict[str, str]] | None = None
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith(("#", "-")):
            if current is not None:
                current.extend(
                    {"alg": "SHA-256", "content": digest.lower()}
                    for digest in _PIP_HASH.findall(line)
                )
            continue
        pin = _PIP_PIN.match(line)
        if not pin:
            raise SbomInputError(f"{PIP_LOCK}: unparseable line {number}: {line!r}")
        name = re.sub(r"[-_.]+", "-", pin.group(1)).lower()
        current = pins.setdefault((name, pin.group(2)), [])
    return [_component("pypi", n, v, h) for (n, v), h in pins.items()]


def _npm_hashes(integrity: str | None) -> list[dict[str, str]]:
    if not integrity:
        return []
    out = []
    for token in integrity.split():
        algo, _, b64 = token.partition("-")
        if algo in NPM_ALGS and b64:
            out.append({"alg": NPM_ALGS[algo], "content": base64.b64decode(b64).hex()})
    return out


def parse_npm_lock(text: str) -> list[dict[str, Any]]:
    """Return npm components from a lockfileVersion 2/3 ``package-lock.json``."""
    try:
        packages = json.loads(text)["packages"]
        if not isinstance(packages, dict):
            raise TypeError("packages is not an object")
    except (ValueError, KeyError, TypeError) as exc:
        raise SbomInputError(f"{NPM_LOCK}: not a lockfile with a 'packages' map ({exc})") from exc
    found: dict[tuple[str, str], list[dict[str, str]]] = {}
    for key, entry in packages.items():
        if not isinstance(entry, dict):
            raise SbomInputError(f"{NPM_LOCK}: package entry {key!r} is not an object")
        if NPM_PREFIX not in key or entry.get("link") or not entry.get("version"):
            continue
        name = key.rsplit(NPM_PREFIX, 1)[1]
        found.setdefault((name, entry["version"]), _npm_hashes(entry.get("integrity")))
    return [_component("npm", n, v, h) for (n, v), h in found.items()]


def _commit_timestamp(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "show", "-s", "--format=%cI", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
        timeout=15,
    )
    raw = result.stdout.strip()
    stamp = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=UTC)
    else:
        stamp = stamp.astimezone(UTC)
    return stamp.strftime("%Y-%m-%dT%H:%M:%SZ")


def build_sbom(repo_root: Path = ROOT) -> dict[str, Any]:
    """Return the SBOM for ``repo_root``.

    Preconditions: both lockfiles exist, parse, and list at least one package each.
    Raises ``SbomInputError`` otherwise.
    """
    pip = parse_pip_lock(_read(repo_root, PIP_LOCK))
    if not pip:
        raise SbomInputError(f"{PIP_LOCK}: no pinned 'name==version' entries found")
    npm = parse_npm_lock(_read(repo_root, NPM_LOCK))
    components = sorted(pip + npm, key=lambda c: c["purl"])
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "timestamp": _commit_timestamp(repo_root),
            "component": {
                "type": "application",
                "name": ROOT_COMPONENT_NAME,
                "version": _git_head(repo_root),
            },
        },
        "components": components,
    }


def render(sbom: dict[str, Any]) -> str:
    """Serialise ``sbom`` to its canonical text form."""
    return json.dumps(sbom, indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output SBOM path")
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="Repository to read")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if the output file is missing or stale vs the current lockfiles/commit",
    )
    args = parser.parse_args(argv)
    try:
        expected = render(build_sbom(args.repo_root))
    except SbomInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.check:
        if not args.out.is_file():
            print(f"missing SBOM: {args.out}", file=sys.stderr)
            return 1
        if args.out.read_text(encoding="utf-8") != expected:
            print(f"stale SBOM: {args.out}", file=sys.stderr)
            return 1
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(expected, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
