"""Load #5590 figure provenance manifest without importing matplotlib figure builders."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "data/core_theory/figure_provenance_manifest.json"


def load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def pinned_figures() -> dict[str, str]:
    data = load_manifest()
    figures = data.get("pinned_figures", {})
    if not isinstance(figures, dict):
        raise TypeError("pinned_figures must be an object")
    return {str(k): str(v) for k, v in figures.items()}
