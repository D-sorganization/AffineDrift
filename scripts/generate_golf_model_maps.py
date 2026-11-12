"""Generate golf model-map reference artifacts from vendored UpstreamDrift MJCF snapshots."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.tools.golf_model_map import (  # noqa: E402
    DEFAULT_JSON_OUT,
    DEFAULT_MANIFEST,
    DEFAULT_QMD_OUT,
    extract_model_map,
    load_manifest,
    maps_to_document,
    render_qmd,
)


def generate(*, check: bool = False) -> bool:
    """Write JSON and Quarto projection, or report whether outputs are current."""
    manifest = load_manifest(DEFAULT_MANIFEST)
    entries = manifest.get("mujoco_models")
    if not isinstance(entries, list):
        msg = "manifest missing mujoco_models array"
        raise ValueError(msg)

    maps = [extract_model_map(repo_root=ROOT, entry=entry) for entry in entries]
    document = maps_to_document(manifest, maps)
    json_text = json.dumps(document, indent=2, sort_keys=True) + "\n"
    qmd_text = render_qmd(manifest, maps)

    if check:
        json_ok = (
            DEFAULT_JSON_OUT.is_file() and DEFAULT_JSON_OUT.read_text(encoding="utf-8") == json_text
        )
        qmd_ok = (
            DEFAULT_QMD_OUT.is_file() and DEFAULT_QMD_OUT.read_text(encoding="utf-8") == qmd_text
        )
        return json_ok and qmd_ok

    DEFAULT_JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_QMD_OUT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_JSON_OUT.write_text(json_text, encoding="utf-8", newline="\n")
    DEFAULT_QMD_OUT.write_text(qmd_text, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit nonzero when outputs are stale")
    args = parser.parse_args()
    if args.check:
        current = generate(check=True)
        if not current:
            print("Golf model-map projection is stale; run without --check.")
            return 1
        print("Golf model-map projection is current.")
        return 0
    generate(check=False)
    print(f"Wrote {DEFAULT_JSON_OUT.relative_to(ROOT)}")
    print(f"Wrote {DEFAULT_QMD_OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
