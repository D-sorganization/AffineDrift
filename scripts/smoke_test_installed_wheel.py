#!/usr/bin/env python3
"""Smoke test for installed AffineDrift wheel outside repository root (#4532).

Verifies that the built wheel can be installed into an isolated directory and
that every public module (especially those importing src.core) imports cleanly
without repository root on sys.path.
"""

from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def find_latest_wheel(dist_dir: Path) -> Path:
    """Find the newest wheel file in the specified dist directory."""
    wheels = sorted(dist_dir.glob("affinedrift-*.whl"), key=lambda p: p.stat().st_mtime)
    if not wheels:
        raise FileNotFoundError(f"No affinedrift-*.whl found in {dist_dir}")
    return wheels[-1]


def verify_wheel_imports(target_dir: Path) -> list[str]:
    """Test importing modules from target_dir where wheel was installed.

    Returns a list of failed module names and reasons.
    """
    python_code = """
import importlib
import logging
import pkgutil
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smoke_verifier")

critical_modules = [
    "src",
    "src.core",
    "src.core.constants",
    "src.core.contracts",
    "src.core.optimizers",
    "src.core.optimizers.ilqr_solver",
    "src.affine_control",
    "src.affine_control.residuals",
    "src.affine_control.dynamics",
    "src.affine_control.swing_optimizer",
    "src.golf_simulation",
    "src.golf_simulation.round_simulator",
    "src.golf_simulation.ball_flight",
    "src.golf_simulation.putting",
    "src.tangent_models",
    "src.tangent_models.examples",
]

failures = []
imported_count = 0
for mod in critical_modules:
    try:
        m = importlib.import_module(mod)
        imported_count += 1
        logger.info("Imported critical module %s successfully", mod)
    except Exception as exc:
        failures.append(f"{mod}: {exc}")

# Next, walk all packages in the installed wheel
src_dir = sys.path[0] + "/src"
try:
    for _, modname, _ in pkgutil.walk_packages([src_dir], prefix="src."):
        # Skip modules that require optional GUI / web dependencies if not installed
        if any(token in modname for token in ["qt_", "streamlit", "notebooks_bridge"]):
            continue
        try:
            importlib.import_module(modname)
            imported_count += 1
        except ModuleNotFoundError as mnfe:
            # Skip if an optional external dependency like streamlit is missing
            if mnfe.name in ["streamlit", "PyQt6", "PyQt5", "PySide6"]:
                continue
            failures.append(f"{modname}: {mnfe}")
        except Exception as exc:
            failures.append(f"{modname}: {exc}")
except Exception as exc:
    failures.append(f"walk_packages: {exc}")

if failures:
    logger.error("Failed imports (%d): %s", len(failures), failures)
    sys.exit(1)

logger.info("All %d tested wheel modules imported successfully!", imported_count)
"""
    # Execute python in a subprocess with cwd outside repository and clean PYTHONPATH
    env = dict(os.environ)
    env["PYTHONPATH"] = str(target_dir)

    with tempfile.TemporaryDirectory() as external_cwd:
        res = subprocess.run(
            [sys.executable, "-c", python_code],
            cwd=external_cwd,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    if res.returncode != 0:
        logger.error("Verification output: %s\nStderr: %s", res.stdout, res.stderr)
        return [res.stderr.strip() or res.stdout.strip()]

    logger.info("Verification stdout:\n%s", res.stdout.strip())
    return []


def run_smoke_test(wheel_path: Path) -> int:
    """Unpack/install wheel in a clean tempdir outside repo and verify imports."""
    logger.info("Testing wheel: %s", wheel_path)

    with tempfile.TemporaryDirectory() as temp_install_dir:
        target = Path(temp_install_dir)
        logger.info("Extracting wheel into %s", target)
        with zipfile.ZipFile(wheel_path, "r") as zf:
            zf.extractall(target)

        failures = verify_wheel_imports(target)
        if failures:
            logger.error("Smoke test failed: %s", failures)
            return 1

    logger.info("Smoke test passed successfully!")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test installed wheel outside repo root.")
    parser.add_argument("--wheel", type=Path, help="Path to wheel to test", default=None)
    parser.add_argument(
        "--dist", type=Path, help="Directory containing wheels", default=Path("dist")
    )
    args = parser.parse_args()

    wheel = args.wheel or find_latest_wheel(args.dist)
    return run_smoke_test(wheel)


if __name__ == "__main__":
    sys.exit(main())
