"""Workflow steps must be able to import the ``scripts`` package they run (#5240).

``python3 scripts/foo.py`` puts ``scripts/`` on ``sys.path``, not the repo
root, so a script that does ``from scripts.x import y`` dies with
``ModuleNotFoundError: No module named 'scripts'`` unless it bootstraps
``sys.path`` itself or the workflow sets ``PYTHONPATH``. Run such scripts as
``python3 -m scripts.foo`` instead.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
_BY_PATH = re.compile(r"python3?\s+(scripts/[\w/]+\.py)")
_PACKAGE_IMPORT = re.compile(r"^(?:from|import) scripts\b", re.MULTILINE)


def _needs_repo_root(script: Path) -> bool:
    """True when ``script`` imports ``scripts.*`` without fixing ``sys.path``."""
    text = script.read_text(encoding="utf-8")
    return bool(_PACKAGE_IMPORT.search(text)) and "sys.path" not in text


def _offenders(workflow: Path) -> list[str]:
    text = workflow.read_text(encoding="utf-8")
    if "PYTHONPATH" in text:
        return []
    found = []
    for rel in sorted(set(_BY_PATH.findall(text))):
        script = REPO_ROOT / rel
        if script.is_file() and _needs_repo_root(script):
            found.append(f"{workflow.name}: python3 {rel}")
    return found


def test_workflows_run_package_importing_scripts_as_modules() -> None:
    offenders = [o for wf in sorted(WORKFLOWS.glob("*.yml")) for o in _offenders(wf)]
    assert not offenders, "run these with `python3 -m scripts.<name>`:\n" + "\n".join(offenders)


def test_detector_flags_a_by_path_call_to_a_package_importing_script(tmp_path: Path) -> None:
    workflow = tmp_path / "wf.yml"
    workflow.write_text("run: python3 scripts/report_e2e_browser_failures.py --x\n")
    assert _offenders(workflow) == ["wf.yml: python3 scripts/report_e2e_browser_failures.py"]
