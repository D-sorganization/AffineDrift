"""Stable identifiers and source-route mappings for claim-audit tooling."""

from __future__ import annotations

import hashlib
from pathlib import Path


def stable_audit_id(route: str) -> str:
    """Return the stable content-derived audit ID for a canonical route."""
    digest = hashlib.sha256(route.encode("utf-8")).hexdigest()[:12]
    return f"ad-route-{digest}"


def source_route(source_path: object) -> str:
    """Map one canonical source path to its public HTML route."""
    return f"/{Path(str(source_path)).with_suffix('.html').as_posix()}"
