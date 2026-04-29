"""Tests for PWA manifest icon sizing consistency."""

from __future__ import annotations

import json
import struct
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]


def _read_png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        if handle.read(8) != b"\x89PNG\r\n\x1a\n":
            msg = f"{path} is not a PNG image"
            raise ValueError(msg)

        while True:
            chunk_len = handle.read(4)
            if not chunk_len:
                break
            chunk_length = struct.unpack(">I", chunk_len)[0]
            chunk_type = handle.read(4)
            chunk_data = handle.read(chunk_length)
            handle.read(4)  # CRC

            if chunk_type == b"IHDR":
                width, height = struct.unpack(">II", chunk_data[:8])
                return width, height

    msg = f"Could not find PNG dimensions in {path}"
    raise ValueError(msg)


def test_manifest_icons_match_declared_sizes() -> None:
    """Each local PNG icon in the manifest should match its declared size."""
    manifest = json.loads((ROOT_DIR / "manifest.json").read_text(encoding="utf-8"))
    icons = manifest.get("icons", [])
    assert isinstance(icons, list)

    for icon in icons:
        src = icon.get("src", "")
        sizes = icon.get("sizes")

        if not src or not sizes or not src.startswith("/"):
            continue
        if str(icon.get("type", "")).lower() != "image/png":
            continue

        icon_path = ROOT_DIR / src.lstrip("/")
        assert icon_path.exists(), f"Manifest icon is missing: {src}"
        width, height = _read_png_size(icon_path)
        declared_width, declared_height = [int(side) for side in sizes.split("x", 1)]
        assert (width, height) == (
            declared_width,
            declared_height,
        ), f"Manifest size for {src} is {sizes}, but file is {width}x{height}"
