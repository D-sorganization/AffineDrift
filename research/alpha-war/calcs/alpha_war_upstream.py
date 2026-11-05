"""Resolve and verify pinned UpstreamDrift dependencies for Alpha War calcs."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import types
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CALCS_DIR = Path(__file__).resolve().parent
LOCK_PATH = CALCS_DIR / "upstream_drift.lock.json"
ENV_ROOT = "ALPHA_WAR_UPSTREAM_DRIFT_ROOT"
WSCG_REL = Path("docs/research/proximal_distal_energy_transfer/data/wscg_two_hand_raw")
WSCG_CASES = ("base", "ztcf", "delta")


class UpstreamDriftReproError(RuntimeError):
    """Raised when UpstreamDrift is missing, misconfigured, or not at the pinned revision."""


@dataclass(frozen=True)
class UpstreamDriftContext:
    """Pinned UpstreamDrift checkout used read-only by the sensitivity suite."""

    root: Path
    commit: str
    input_sha256: dict[str, str]


def load_lock() -> dict[str, Any]:
    """Load ``upstream_drift.lock.json``."""
    if not LOCK_PATH.is_file():
        raise UpstreamDriftReproError(f"Missing dependency lock: {LOCK_PATH}")
    return json.loads(LOCK_PATH.read_text(encoding="utf-8"))


def resolve_upstream_root() -> Path:
    """Return the UpstreamDrift checkout path from ``ALPHA_WAR_UPSTREAM_DRIFT_ROOT``."""
    raw = os.environ.get(ENV_ROOT, "").strip()
    if not raw:
        raise UpstreamDriftReproError(
            f"Set {ENV_ROOT} to a local clone of "
            f"{load_lock().get('repository', 'D-sorganization/UpstreamDrift')} "
            f"at commit {load_lock().get('commit', '(see lock file)')[:12]}…"
        )
    root = Path(raw).expanduser().resolve()
    if not root.is_dir():
        raise UpstreamDriftReproError(f"{ENV_ROOT} is not a directory: {root}")
    return root


def _git_head(root: Path) -> str:
    proc = subprocess.run(  # noqa: S603
        ["git", "-C", str(root), "rev-parse", "HEAD"],  # noqa: S607
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise UpstreamDriftReproError(
            f"UpstreamDrift at {root} is not a git checkout: {proc.stderr.strip()}"
        )
    return proc.stdout.strip()


def verify_pinned_commit(root: Path, lock: dict[str, Any] | None = None) -> str:
    """Ensure ``root`` is checked out at the commit recorded in the lock file."""
    lock = lock or load_lock()
    expected = str(lock["commit"])
    head = _git_head(root)
    if head != expected and not head.startswith(expected[:12]):
        raise UpstreamDriftReproError(
            f"UpstreamDrift pin mismatch: lock expects {expected[:12]}… but HEAD is {head[:12]}…"
        )
    return head


def sha256_file(path: Path) -> str:
    """Return hex SHA-256 digest of ``path``."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def wscg_csv_hashes(root: Path, lock: dict[str, Any] | None = None) -> dict[str, str]:
    """Hash WSCG CSV inputs relative to ``root`` and verify against the lock when present."""
    lock = lock or load_lock()
    expected = lock.get("wscg_input_sha256", {})
    hashes: dict[str, str] = {}
    for case in WSCG_CASES:
        rel = WSCG_REL / f"{case}.csv"
        path = root / rel
        if not path.is_file():
            raise UpstreamDriftReproError(f"Missing WSCG dataset: {path}")
        digest = sha256_file(path)
        hashes[str(rel)] = digest
        locked = expected.get(str(rel))
        if locked is not None and locked != digest:
            raise UpstreamDriftReproError(
                f"WSCG input hash mismatch for {rel}: lock {locked[:12]}… vs {digest[:12]}…"
            )
    return hashes


def bootstrap_namespace_packages(root: Path) -> None:
    """Register read-only namespace packages so UpstreamDrift scripts import without GUI init."""
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    for pkg_name, pkg_paths in [
        ("src", [str(root / "src")]),
        ("src.shared", [str(root / "src/shared")]),
        ("src.shared.python", [str(root / "src/shared/python")]),
        (
            "src.shared.python.biomechanics",
            [str(root / "src/shared/python/biomechanics")],
        ),
    ]:
        if pkg_name not in sys.modules:
            module = types.ModuleType(pkg_name)
            module.__path__ = pkg_paths
            sys.modules[pkg_name] = module


def prepare_upstream_context(*, verify_inputs: bool = True) -> UpstreamDriftContext:
    """Resolve path, verify pin, optionally verify dataset hashes, and bootstrap imports."""
    lock = load_lock()
    root = resolve_upstream_root()
    commit = verify_pinned_commit(root, lock)
    input_sha256 = wscg_csv_hashes(root, lock) if verify_inputs else {}
    bootstrap_namespace_packages(root)
    return UpstreamDriftContext(root=root, commit=commit, input_sha256=input_sha256)


def build_generation_provenance(
    ctx: UpstreamDriftContext,
    *,
    suite_version: str,
    studies: dict[str, Any],
) -> dict[str, Any]:
    """Build provenance metadata for a regeneration run."""
    lock = load_lock()
    studies_sha256 = hashlib.sha256(json.dumps(studies, indent=2).encode("utf-8")).hexdigest()
    return {
        "upstream_repository": lock.get("repository"),
        "upstream_commit": ctx.commit,
        "upstream_root_env": ENV_ROOT,
        "wscg_input_sha256": ctx.input_sha256,
        "suite_module": "alpha_war_sensitivity_suite.py",
        "suite_version": suite_version,
        "output_json": "alpha_war_calculations.json",
        "studies_sha256": studies_sha256,
        "python_version": sys.version.split()[0],
    }
