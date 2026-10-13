"""Tools companion catalog generator (ISSUE-4127).

Generates repositories/tools.qmd from Tools tools.json registry following
the programming companion architecture.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

PINNED_TOOLS_SHA = "f0112a4b76ff904c88733532c55bfbfc2d115e5c"
PINNED_TOOLS_DATE = "2026-10-12"


def load_tools_registry(path: Path) -> dict[str, list[dict[str, Any]]]:
    """Load tools registry from a json file."""
    if not path.is_file():
        raise FileNotFoundError(f"Tools registry not found at {path}")
    with open(path, encoding="utf-8") as f:
        data: dict[str, list[dict[str, Any]]] = json.load(f)
    return data


def render_tools_qmd(registry: dict[str, list[dict[str, Any]]]) -> str:
    """Render repositories/tools.qmd content from registry."""
    total_tools = sum(len(items) for items in registry.values())
    categories_count = len(registry)
    sha_short = PINNED_TOOLS_SHA[:8]
    gh_tree = f"https://github.com/D-sorganization/Tools/tree/{PINNED_TOOLS_SHA}"

    desc = (
        "Desktop and web tools catalog for biomechanics, robotics, kinematics, "
        "data processing, and simulation from the Tools repository."
    )

    lines: list[str] = [
        "---",
        'title: "Tools Repository"',
        f'description: "{desc}"',
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
        (
            '          The <a href="https://github.com/D-sorganization/Tools" '
            'target="_blank" rel="noopener">Tools<span class="sr-only">'
            "(opens in a new tab)</span></a>"
        ),
        (
            "          repository is the D-sorganization fleet's canonical suite "
            "of PyQt6 desktop tools, browser applications,"
        ),
        (
            "          and computational utilities. Spanning biomechanics, robotics, "
            "motion capture, data processing, and numerical physics,"
        ),
        (
            "          it provides both interactive user interfaces and verified "
            "calculation backends."
        ),
        "        </p>",
        '        <p class="resource-description">',
        (
            "          <strong>Authority snapshot.</strong> This catalog reflects the "
            "Tools repository at protected <code>main</code> commit "
        ),
        (
            f'          <a href="{gh_tree}" target="_blank" rel="noopener">'
            f"<code>{sha_short}</code><span class="
            '"sr-only">(opens in a new tab)</span></a>, '
        ),
        (
            f"          reviewed {PINNED_TOOLS_DATE}. It covers {total_tools} "
            f"declared tool interfaces across {categories_count} functional categories."
        ),
        "        </p>",
        '        <div class="site-card site-card--callout u-mb-2">',
        '          <h2 class="u-mb-1">Authority Boundary</h2>',
        '          <p class="resource-description">',
        (
            "            <strong>This establishes</strong> an indexed catalog of "
            "desktop and web tools, launch surfaces, and implementation paths."
        ),
        "          </p>",
        '          <p class="resource-description">',
        (
            "            <strong>This does not establish</strong> independent "
            "clinical efficacy, human injury prevention validation, "
            "or commercial equipment certification without empirical testing."
        ),
        "          </p>",
        "        </div>",
        "      </div>",
        "",
        '      <div class="resource-card">',
        "        <h2>Site Parity &amp; Mirrored Tools</h2>",
        '        <p class="resource-description">',
        (
            "          Two canonical tools in this repository have dedicated "
            "representations on AffineDrift:"
        ),
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
        (
            "                <td><strong>Rotation Representation Converter</strong> "
            "(<code>rotation_converter</code>)</td>"
        ),
        ("                <td><code>PyQt6</code> " "<code>Web</code></td>"),
        (
            '                <td><a href="../articles/rotation-converter.html">'
            "Rotation Representation Converter</a></td>"
        ),
        (
            "                <td>Automated golden-vector parity test suite "
            "(<code>tests/rotation-converter-parity.test.js</code>) against canonical "
            "quaternion/matrix algorithms.</td>"
        ),
        "              </tr>",
        "              <tr>",
        (
            "                <td><strong>Rate of Closure Impact Explorer</strong> "
            "(<code>rate_of_closure</code>)</td>"
        ),
        ("                <td><code>PyQt6</code> " "<code>Web</code></td>"),
        (
            '                <td><a href="../pages/tools.html">'
            "Programs &amp; Tools</a> (T-10 exploration)</td>"
        ),
        (
            "                <td>Kinematic delivery discrepancy analysis between clubhead "
            "center of mass and geometric center.</td>"
        ),
        "              </tr>",
        "            </tbody>",
        "          </table>",
        "        </div>",
        "      </div>",
    ]

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
            desc_text = html.escape(tool.get("desc", ""))
            path_str = html.escape(tool.get("path", ""))

            id_cell = (
                f"                <td><strong>{name}</strong><br>"
                f'<small class="text-muted"><code>{tool_id}</code></small></td>'
            )
            surf_cell = f"                <td><code>{surface}</code></td>"
            mat_cell = f"                <td><code>{maturity}</code></td>"
            desc_cell = f"                <td>{desc_text}</td>"
            path_cell = f"                <td><small><code>{path_str}</code></small></td>"

            lines.extend(
                [
                    "              <tr>",
                    id_cell,
                    surf_cell,
                    mat_cell,
                    desc_cell,
                    path_cell,
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

    gh_link = (
        '          <a href="https://github.com/D-sorganization/Tools" '
        'target="_blank" rel="noopener" class="resource-link">'
        'View on GitHub →<span class="sr-only">(opens in a new tab)</span></a>'
        '<span class="u-text-muted"> (navigation only; not pinned to a specific commit)</span>'
    )

    lines.extend(
        [
            "",
            '      <div class="resource-card">',
            "        <h2>Repository Access</h2>",
            '        <p class="resource-description">',
            "          The Tools repository is hosted on GitHub:",
            "          <br><br>",
            gh_link,
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
