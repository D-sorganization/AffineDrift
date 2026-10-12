"""Generate or verify the Tools repository catalog page (repositories/tools.qmd).

Consumes data/tools/tools.json (Tools repository registry) and generates
repositories/tools.qmd with governed capability tables and authority boundaries.

Usage::

    python -m scripts.generate_tools_catalog          # rewrite repositories/tools.qmd
    python -m scripts.generate_tools_catalog --check  # fail if stale
"""

from __future__ import annotations

import argparse
import html
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY_PATH = REPO_ROOT / "data" / "tools" / "tools.json"
FALLBACK_REGISTRY_PATH = REPO_ROOT.parent / "Tools" / "tools.json"
OUTPUT_PATH = REPO_ROOT / "repositories" / "tools.qmd"

PINNED_TOOLS_SHA = "f0112a4b76ff904c88733532c55bfbfc2d115e5c"
PINNED_TOOLS_DATE = "2026-10-12"


def load_tools_registry(path: Path | None = None) -> dict[str, list[dict[str, Any]]]:
    """Load tools registry from primary or fallback path."""
    target = path or (
        DEFAULT_REGISTRY_PATH if DEFAULT_REGISTRY_PATH.is_file() else FALLBACK_REGISTRY_PATH
    )
    if not target.is_file():
        raise FileNotFoundError(f"Tools registry not found at {target}")
    with open(target, encoding="utf-8") as f:
        data: dict[str, list[dict[str, Any]]] = json.load(f)
    return data


def render_tools_qmd(registry: dict[str, list[dict[str, Any]]]) -> str:
    """Render repositories/tools.qmd content from registry."""
    total_tools = sum(len(items) for items in registry.values())
    categories_count = len(registry)

    lines: list[str] = [
        "---",
        'title: "Tools Repository"',
        'description: "Desktop and web tools catalog for biomechanics, robotics, kinematics, data processing, and simulation from the Tools repository."',
        "page-layout: full",
        f'pinned_tools_sha: "{PINNED_TOOLS_SHA}"',
        f'pinned_tools_reviewed: "{PINNED_TOOLS_DATE}"',
        "categories:",
        "- tools",
        "- models",
        "---",
        "",
        "```{=html}",
        '<section class="resources-section">',
        '  <div class="ad-page-container">',
        '    <div class="resource-grid">',
        '      <div class="resource-card">',
        '        <h1 class="section-heading">Tools Repository</h1>',
        '        <p class="resource-description">',
        '          The <a href="https://github.com/D-sorganization/Tools" target="_blank" rel="noopener">Tools<span class="sr-only">(opens in a new tab)</span></a>',
        "          repository is the D-sorganization fleet's canonical suite of PyQt6 desktop tools, browser applications,",
        "          and computational utilities. Spanning biomechanics, robotics, motion capture, data processing, and numerical physics,",
        "          it provides both interactive user interfaces and verified calculation backends.",
        "        </p>",
        '        <p class="resource-description">',
        "          <strong>Authority snapshot.</strong> This catalog reflects the Tools repository at protected <code>main</code> commit ",
        f'          <a href="https://github.com/D-sorganization/Tools/tree/{PINNED_TOOLS_SHA}" target="_blank" rel="noopener"><code>{PINNED_TOOLS_SHA[:8]}</code><span class="sr-only">(opens in a new tab)</span></a>, ',
        f"          reviewed {PINNED_TOOLS_DATE}. It covers {total_tools} declared tool interfaces across {categories_count} functional categories.",
        "        </p>",
        '        <div class="site-card site-card--callout u-mb-2">',
        '          <h2 class="u-mb-1">Authority Boundary</h2>',
        '          <p class="resource-description">',
        "            <strong>This establishes</strong> an indexed catalog of desktop and web tools, launch surfaces, and implementation paths.",
        "          </p>",
        '          <p class="resource-description">',
        "            <strong>This does not establish</strong> independent clinical efficacy, human injury prevention validation, or commercial equipment certification without empirical testing.",
        "          </p>",
        "        </div>",
        "      </div>",
        "",
        '      <div class="resource-card">',
        "        <h2>Site Parity &amp; Mirrored Tools</h2>",
        '        <p class="resource-description">',
        "          Two canonical tools in this repository have dedicated representations on AffineDrift:",
        "        </p>",
        '        <div class="table-responsive u-mt-2">',
        '          <table class="table">',
        "            <thead>",
        "              <tr>",
        "                <th>Tool</th>",
        "                <th>Surface</th>",
        "                <th>Site Representation</th>",
        "                <th>Parity Verification</th>",
        "              </tr>",
        "            </thead>",
        "            <tbody>",
        "              <tr>",
        "                <td><strong>Rotation Representation Converter</strong> (<code>rotation_converter</code>)</td>",
        '                <td><span class="badge bg-secondary">PyQt6</span> <span class="badge bg-info text-dark">Web</span></td>',
        '                <td><a href="../articles/rotation-converter.html">Rotation Representation Converter</a></td>',
        "                <td>Automated golden-vector parity test suite (<code>tests/rotation-converter-parity.test.js</code>) against canonical quaternion/matrix algorithms.</td>",
        "              </tr>",
        "              <tr>",
        "                <td><strong>Rate of Closure Impact Explorer</strong> (<code>rate_of_closure</code>)</td>",
        '                <td><span class="badge bg-secondary">PyQt6</span> <span class="badge bg-info text-dark">Web</span></td>',
        '                <td><a href="../pages/tools.html">Programs &amp; Tools</a> (T-10 exploration)</td>',
        "                <td>Kinematic delivery discrepancy analysis between clubhead center of mass and geometric center.</td>",
        "              </tr>",
        "            </tbody>",
        "          </table>",
        "        </div>",
        "      </div>",
    ]

    # Generate category blocks
    for category, tools in sorted(registry.items()):
        escaped_category = html.escape(category)
        lines.extend(
            [
                "",
                '      <div class="resource-card">',
                f"        <h2>{escaped_category}</h2>",
                '        <div class="table-responsive">',
                '          <table class="table">',
                "            <thead>",
                "              <tr>",
                "                <th>Tool</th>",
                "                <th>Surface</th>",
                "                <th>Maturity</th>",
                "                <th>Description</th>",
                "                <th>Path</th>",
                "              </tr>",
                "            </thead>",
                "            <tbody>",
            ]
        )
        for tool in tools:
            name = html.escape(tool.get("name", ""))
            tool_id = html.escape(tool.get("tool_id", ""))
            surface = html.escape(tool.get("surface", "pyqt6"))
            maturity = html.escape(tool.get("maturity", "stable"))
            desc = html.escape(tool.get("desc", ""))
            path_str = html.escape(tool.get("path", ""))

            surface_badge = "bg-info text-dark" if surface == "web" else "bg-secondary"
            maturity_badge = (
                "bg-success"
                if maturity == "stable"
                else ("bg-warning text-dark" if maturity == "beta" else "bg-light text-dark")
            )

            lines.extend(
                [
                    "              <tr>",
                    f'                <td><strong>{name}</strong><br><small class="text-muted"><code>{tool_id}</code></small></td>',
                    f'                <td><span class="badge {surface_badge}">{surface}</span></td>',
                    f'                <td><span class="badge {maturity_badge}">{maturity}</span></td>',
                    f"                <td>{desc}</td>",
                    f"                <td><small><code>{path_str}</code></small></td>",
                    "              </tr>",
                ]
            )

        lines.extend(
            [
                "            </tbody>",
                "          </table>",
                "        </div>",
                "      </div>",
            ]
        )

    lines.extend(
        [
            "",
            '      <div class="resource-card">',
            "        <h2>Repository Access</h2>",
            '        <p class="resource-description">',
            "          The Tools repository is hosted on GitHub:",
            "          <br><br>",
            '          <a href="https://github.com/D-sorganization/Tools" target="_blank" rel="noopener" class="resource-link">View on GitHub →<span class="sr-only">(opens in a new tab)</span></a><span class="u-text-muted"> (navigation only; not pinned to a specific commit)</span>',
            "          <br><br>",
            "          <strong>Clone with Git:</strong><br>",
            "          <code>git clone https://github.com/D-sorganization/Tools.git</code>",
            "        </p>",
            "      </div>",
            "    </div>",
            "  </div>",
            "</section>",
            "```",
            "",
            "## Related Articles",
            "",
            "- [Programs & Tools](../pages/tools.html)",
            "- [Rotation Representation Converter](../articles/rotation-converter.html)",
            "- [Repositories](repositories.html)",
            "- [Model Repositories](repositories-models.html)",
            "- [Modeling Suite](../models/models.html)",
            "",
        ]
    )

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="fail if output differs from generated"
    )
    parser.add_argument("--registry", type=Path, default=None, help="path to tools.json")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    registry = load_tools_registry(args.registry)
    rendered = render_tools_qmd(registry)

    if args.check:
        if not OUTPUT_PATH.is_file():
            logger.error(
                "%s does not exist; run python -m scripts.generate_tools_catalog", OUTPUT_PATH
            )
            return 1
        current = OUTPUT_PATH.read_text(encoding="utf-8")
        if current != rendered:
            logger.error("%s is stale; run python -m scripts.generate_tools_catalog", OUTPUT_PATH)
            return 1
        logger.info("%s is current.", OUTPUT_PATH.relative_to(REPO_ROOT))
        return 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(rendered, encoding="utf-8", newline="\n")
    logger.info("Wrote %s", OUTPUT_PATH.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
