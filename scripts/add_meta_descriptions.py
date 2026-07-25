#!/usr/bin/env python3
"""Add meta descriptions to chapter/article files missing them.

The updater prefers existing manual overrides, then falls back to a concise
first meaningful paragraph from the file body.
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.tools.utils.content_utils import (  # noqa: E402  # reason: import ordering constraint
    read_qmd_with_frontmatter,
)

# Manual overrides for better descriptions
DESCRIPTION_OVERRIDES = {
    "articles/theory-part1.qmd": "Foundational derivation showing the golf swing as a control-affine mechanical system, introducing the drift/input decomposition framework for biomechanical analysis.",
    "articles/theory-part2.qmd": "Diagnostic tools for analyzing golf swing dynamics: the Zero Torque Counterfactual (ZTCF) and Zero Velocity Counterfactual (ZVCF) for separating passive and active forces.",
    "articles/theory-part3.qmd": "Establishes drift invariance properties and develops a taxonomy of forces in the golf swing, analyzing the limitations of the affine control assumption.",
    "articles/theory-part4.qmd": "Modal approximations, wrench decomposition, and pendulum dynamics with detailed mathematical derivations for golf swing biomechanics.",
    "articles/theory-part5.qmd": "Simulink implementation documentation for the control-affine golf swing model, including numerical routines and validation approaches.",
    "articles/affine-nature-golf-swing.qmd": "Comprehensive theoretical foundation establishing the golf swing as a control-affine system, with detailed analysis of drift dynamics, input superposition, and causal force decomposition.",
    "articles/superposition.qmd": "Rigorous derivation of input superposition in affine control systems using Newton-Euler, Lagrangian, and screw-theoretic formulations with applications to biomechanics.",
    "articles/controllability-drift-ratio.qmd": "Analysis of the drift-to-control ratio in golf swings using control theory, multibody dynamics, and relativistic analogies to understand passive dynamics exploitation.",
    "articles/drift-components-wrench-double-pendulum.qmd": "Decomposition of natural versus active forces and torques in affine mechanical systems, with applications to double pendulum golf swing models.",
    "articles/force-mobility-matrices.qmd": "Force and mobility ellipsoid analysis for the golf swing, providing geometric insights into directional strength and movement capabilities.",
    "articles/intentional-constraint-collapse.qmd": "Analysis of how golfers generate high impact forces while maintaining stable club motion through intentional constraint release at ball contact.",
    "articles/inverse-dynamics.qmd": "Critical examination of inverse dynamics limitations in biomechanics, explaining why calculated torques don't represent actual muscle contributions.",
    "articles/inverse-dynamics-inference.qmd": "Inference challenges in applying inverse dynamics to nonlinear affine systems, with implications for golf swing biomechanical analysis.",
    "articles/lagrangian-reference.qmd": "Reference guide for Lagrangian mechanics applied to control-affine multibody systems, bridging classical mechanics and modern control theory.",
    "articles/nonlinear-control-insights.qmd": "Insights from nonlinear control theory on drift causality in golf biomechanics, with future research directions for the control-affine framework.",
    "articles/null-space-constraint-jacobian.qmd": "Analysis of unconstrained motion within constrained biomechanical systems using null space projections, applied to golf swing joint coordination.",
    "articles/screw-theory-reference.qmd": "Reference guide for screw theory notation and concepts in control-affine multibody dynamics, including twists, wrenches, and exponential coordinates.",
    "articles/secondary-axis-stability.qmd": "Mechanical analysis of secondary axis rotation stability in golf clubs, with implications for putter design and face angle consistency.",
    "articles/strokes-gained-limitations.qmd": "Statistical and methodological limitations of strokes gained analysis for individual golfer assessment, with recommendations for proper interpretation.",
    "articles/wrist-universal-joint.qmd": "Biomechanical model of the left wrist as a universal joint, analyzing how grip angle influences force transmission and clubface angle variability.",
    "articles/appendix-applications.qmd": "Practical applications of the control-affine decomposition framework in golf swing analysis, training, and equipment design.",
}

TARGET_ROOTS = (ROOT / "articles", ROOT / "content")
EDITORIAL_ONLY_FILENAMES = {"INLINE_SUGGESTIONS.md"}


def extract_first_paragraph(content: str) -> str:
    """Extract first meaningful paragraph for description."""
    # Remove frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            content = parts[2]

    # Remove abstracts, code blocks, HTML
    content = re.sub(r":::.*?:::", "", content, flags=re.DOTALL)
    content = re.sub(r"```[\s\S]*?```", "", content)
    content = re.sub(r"<[^>]+>", "", content)
    content = re.sub(r"^#+\s+.+$", "", content, flags=re.MULTILINE)
    content = re.sub(r"\$\$[\s\S]*?\$\$", "", content)
    content = re.sub(r"\$[^$]+\$", " ", content)

    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    for p in paragraphs:
        if p.lstrip().startswith(">"):
            continue
        clean_p = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", p)
        clean_p = re.sub(r"\s+", " ", clean_p).strip()
        clean_p = re.sub(r"[*_]", "", clean_p)
        if len(clean_p) > 80 and not clean_p.startswith("!") and not clean_p.startswith("{"):
            # Truncate to ~155 chars at word boundary
            if len(clean_p) > 155:
                clean_p = clean_p[:155].rsplit(" ", 1)[0] + "..."
            return clean_p

    return ""


def extract_title(content: str) -> str:
    """Extract the first Markdown H1 title from body content."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            content = parts[2]

    title_match = re.search(r"^#\s+(.+?)\s*$", content, flags=re.MULTILINE)
    if not title_match:
        return ""
    return re.sub(r"\s+", " ", title_match.group(1)).strip()


def build_critique_description(content: str) -> str:
    """Build a concise, unique description for public critique pages."""
    title = extract_title(content)
    if not title:
        return ""

    topic = re.sub(r"^(Critique|Bibliographic Analysis):\s*", "", title).strip()
    if title.startswith("Bibliographic Analysis:"):
        return f"Bibliographic analysis supporting the AffineDrift critique of {topic}."
    return (
        f"Critique and response context for {topic} in AffineDrift's "
        "control-affine golf-swing framework."
    )


def build_description(filepath: Path, content: str, frontmatter: dict[str, str]) -> str:
    """Build a conservative description for a file."""
    relpath = filepath.relative_to(ROOT).as_posix()
    if relpath in DESCRIPTION_OVERRIDES:
        return DESCRIPTION_OVERRIDES[relpath]

    if relpath.startswith("critiques/"):
        description = build_critique_description(content)
        if description:
            return description

    description = extract_first_paragraph(content)
    if description:
        return description

    title = frontmatter.get("title", "").strip()
    if title:
        return title

    return ""


def _escape_yaml_string(value: str) -> str:
    """Escape a value for a compact double-quoted YAML scalar."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def add_description_to_file(filepath: Path, description: str) -> bool:
    """Add description to frontmatter of a file."""
    content = filepath.read_text(encoding="utf-8")

    if not content.startswith("---"):
        title = extract_title(content)
        if not title:
            return False
        escaped_title = _escape_yaml_string(title)
        escaped_desc = _escape_yaml_string(description)
        filepath.write_text(
            f'---\ntitle: "{escaped_title}"\ndescription: "{escaped_desc}"\n---\n\n{content}',
            encoding="utf-8",
        )
        return True

    parts = content.split("---", 2)
    if len(parts) < 3:
        return False

    frontmatter = parts[1]

    # Check if description already exists
    if re.search(r"^description:", frontmatter, re.MULTILINE):
        return False

    # Find where to insert (after title)
    lines = frontmatter.strip().split("\n")
    new_lines = []
    inserted = False

    for line in lines:
        new_lines.append(line)
        if line.startswith("title:") and not inserted:
            escaped_desc = _escape_yaml_string(description)
            new_lines.append(f'description: "{escaped_desc}"')
            inserted = True

    if not inserted:
        # Add at end if no title found
        escaped_desc = _escape_yaml_string(description)
        new_lines.append(f'description: "{escaped_desc}"')

    new_frontmatter = "\n".join(new_lines)
    new_content = f"---\n{new_frontmatter}\n---{parts[2]}"

    filepath.write_text(new_content, encoding="utf-8")
    return True


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "roots",
        nargs="*",
        type=Path,
        help="Optional content roots to update. Defaults to articles/ and content/.",
    )
    return parser.parse_args()


def main() -> None:
    """Add descriptions to all files missing them."""
    args = parse_args()
    target_roots = tuple((ROOT / root).resolve() for root in args.roots) or TARGET_ROOTS
    files_updated = 0
    files_skipped = 0

    for target_root in target_roots:
        if not target_root.exists():
            continue

        for filepath in sorted(target_root.rglob("*")):
            if filepath.suffix.lower() not in {".qmd", ".md"}:
                continue
            if filepath.name in EDITORIAL_ONLY_FILENAMES:
                files_skipped += 1
                continue

            content, frontmatter = read_qmd_with_frontmatter(filepath)
            if "description" in frontmatter:
                files_skipped += 1
                continue

            if not frontmatter.get("title") and not extract_title(content):
                files_skipped += 1
                continue

            description = build_description(filepath, content, frontmatter)
            if not description:
                files_skipped += 1
                continue

            if add_description_to_file(filepath, description):
                files_updated += 1
            else:
                files_skipped += 1

    print(f"Updated {files_updated} files; skipped {files_skipped}.")


if __name__ == "__main__":
    main()
