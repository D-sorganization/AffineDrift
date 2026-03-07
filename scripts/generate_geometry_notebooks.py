"""Generate chapter-aligned notebooks for The Geometry of Motion."""

from __future__ import annotations

from pathlib import Path

from src.tools.notebooks_bridge import sync_notebook_bridge


def main() -> None:
    """Run notebook bridge sync in repository root."""
    repo_root = Path(__file__).resolve().parents[1]
    output_dir = repo_root / "notebooks" / "geometry_of_motion"
    manifest_path = output_dir / "manifest.json"
    sync_notebook_bridge(repo_root=repo_root, output_dir=output_dir, manifest_path=manifest_path)


if __name__ == "__main__":
    main()
