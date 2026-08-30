"""Generate or verify the governed proximal-distal falsification atlas."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.affine_control.falsification_atlas import (  # noqa: E402  # reason: import ordering constraint
    AtlasPaths,
    load_atlas,
    render_atlas,
)


def canonical_paths(root: Path = ROOT) -> AtlasPaths:
    """Return the repository's canonical atlas authority paths."""
    return AtlasPaths(
        root=root,
        mapping=root / "data/trust/proximal_distal_falsification_atlas.json",
        schema=root / "schemas/proximal-distal-falsification-atlas-v1.schema.json",
        claims=root
        / "articles/proximal_distal_energy_transfer/data/claim_adjudication_summary.json",
        critiques=root / "data/trust/claim_critique_ledger.json",
        source_manifest=root / "articles/proximal_distal_energy_transfer/source_manifest.json",
        readiness=root / "data/research_protocols/library.json",
        output=root / "articles/_generated/proximal-distal-falsification-atlas.qmd",
    )


def generate(paths: AtlasPaths, check: bool = False) -> bool:
    """Write the deterministic projection or report whether it is current."""
    rendered = render_atlas(load_atlas(paths))
    if check:
        return paths.output.is_file() and paths.output.read_text(encoding="utf-8") == rendered
    paths.output.parent.mkdir(parents=True, exist_ok=True)
    paths.output.write_text(rendered, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    """Run the command-line generator in write or check mode."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if output is stale")
    args = parser.parse_args()
    current = generate(canonical_paths(), check=args.check)
    if args.check and not current:
        print("Falsification atlas projection is stale.")
        return 1
    print("Falsification atlas projection is current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
