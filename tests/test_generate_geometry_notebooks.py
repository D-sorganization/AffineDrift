"""Tests for geometry notebook generation orchestration."""

from __future__ import annotations

from pathlib import Path

from scripts import generate_geometry_notebooks


def test_main_invokes_notebook_bridge_with_repo_paths(monkeypatch) -> None:
    """The script should call the bridge with repo-root-derived output paths."""
    calls: list[dict[str, Path]] = []

    def record_sync(*, repo_root: Path, output_dir: Path, manifest_path: Path) -> None:
        calls.append(
            {
                "repo_root": repo_root,
                "output_dir": output_dir,
                "manifest_path": manifest_path,
            }
        )

    monkeypatch.setattr(generate_geometry_notebooks, "sync_notebook_bridge", record_sync)

    generate_geometry_notebooks.main()

    assert len(calls) == 1
    repo_root = calls[0]["repo_root"]
    assert repo_root == Path(generate_geometry_notebooks.__file__).resolve().parents[1]
    assert calls[0]["output_dir"] == repo_root / "notebooks" / "geometry_of_motion"
    assert calls[0]["manifest_path"] == calls[0]["output_dir"] / "manifest.json"
