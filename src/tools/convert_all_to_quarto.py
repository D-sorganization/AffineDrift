#!/usr/bin/env python3
"""Batch LaTeX to Quarto Converter for AffineDrift
Converts all LaTeX article files to Quarto .qmd format.
"""

import os
import sys
from pathlib import Path

from latex_to_qmd import LaTeXToQuartoConverter

# Add project root to sys.path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.tools.utils import setup_logging

logger = setup_logging(__name__)

# Articles directory for Quarto documents
ARTICLES_DIR = "articles"

# Mapping of LaTeX files to their Quarto output locations
CONVERSIONS = [
    # Already converted - keeping for reference
    {
        "source": "content/Wrist as Universal Joint/Wrist_Universal_Claude.tex",
        "target": f"{ARTICLES_DIR}/wrist-universal-joint.qmd",
        "description": "Wrist as Universal Joint article",
    },
    {
        "source": (
            "content/Inverse Dynamics Analysis/Drafts/Inverse Dynamics Claude Current/"
            "inverse_dynamics_final.tex"
        ),
        "target": f"{ARTICLES_DIR}/inverse-dynamics.qmd",
        "description": "Inverse Dynamics article",
    },
    # Affine Background Articles
    {
        "source": "content/Affine Background Articles/Nonlinear_Control_Insights.tex",
        "target": f"{ARTICLES_DIR}/nonlinear-control-insights.qmd",
        "description": "Nonlinear Control Theory Insights",
    },
    {
        "source": "content/Affine Background Articles/Force_Mobility_Matrices.tex",
        "target": f"{ARTICLES_DIR}/force-mobility-matrices.qmd",
        "description": "Force Mobility Matrices",
    },
    {
        "source": "content/Affine Background Articles/Inverse_Dynamics_Inference.tex",
        "target": f"{ARTICLES_DIR}/inverse-dynamics-inference.qmd",
        "description": "Inverse Dynamics Inference",
    },
    {
        "source": "content/Affine Background Articles/Lagrangian_Reference.tex",
        "target": f"{ARTICLES_DIR}/lagrangian-reference.qmd",
        "description": "Lagrangian Reference",
    },
    {
        "source": "content/Affine Background Articles/ScrewTheory_Reference.tex",
        "target": f"{ARTICLES_DIR}/screw-theory-reference.qmd",
        "description": "Screw Theory Reference",
    },
    {
        "source": "content/Affine Background Articles/null_space_constraint_jacobian.tex",
        "target": f"{ARTICLES_DIR}/null-space-constraint-jacobian.qmd",
        "description": "Null Space Constraint Jacobian",
    },
    # Affine Nature of the Golf Swing
    {
        "source": "content/Affine Nature of the Golf Swing/Draft3_Compiled_Working_Copy.tex",
        "target": f"{ARTICLES_DIR}/affine-nature-golf-swing.qmd",
        "description": "Affine Nature of the Golf Swing (Main Article)",
    },
    {
        "source": (
            "content/Affine Nature of the Golf Swing/Appendix_A_Nonlinear_Control_Insights.tex"
        ),
        "target": f"{ARTICLES_DIR}/appendix-nonlinear-control-insights.qmd",
        "description": "Appendix A: Nonlinear Control Insights",
    },
    {
        "source": (
            "content/Affine Nature of the Golf Swing/Appendix_B_Inverse_Dynamics_Inference.tex"
        ),
        "target": f"{ARTICLES_DIR}/appendix-inverse-dynamics-inference.qmd",
        "description": "Appendix B: Inverse Dynamics Inference",
    },
    {
        "source": "content/Affine Nature of the Golf Swing/Appendix_C_Applications.tex",
        "target": f"{ARTICLES_DIR}/appendix-applications.qmd",
        "description": "Appendix C: Applications",
    },
    {
        "source": ("content/Affine Nature of the Golf Swing/Appendix_D_Lagrangian_Reference.tex"),
        "target": f"{ARTICLES_DIR}/appendix-lagrangian-reference.qmd",
        "description": "Appendix D: Lagrangian Reference",
    },
    {
        "source": ("content/Affine Nature of the Golf Swing/Appendix_E_ScrewTheory_Reference.tex"),
        "target": f"{ARTICLES_DIR}/appendix-screw-theory-reference.qmd",
        "description": "Appendix E: Screw Theory Reference",
    },
]


def setup_articles_directory() -> None:
    """Create articles directory if it doesn't exist."""
    os.makedirs(ARTICLES_DIR, exist_ok=True)

    # Create _metadata.yml for articles
    metadata_path = os.path.join(ARTICLES_DIR, "_metadata.yml")
    if not os.path.exists(metadata_path):
        with open(metadata_path, "w") as f:
            f.write(
                """# Shared metadata for all articles
format:
  html:
    toc: true
    toc-depth: 3
    number-sections: false
    code-fold: true
    css: ../styles.css
""",
            )


def convert_all(dry_run: bool = False) -> bool:
    """Convert all LaTeX files to Quarto."""
    converter = LaTeXToQuartoConverter()

    if dry_run:
        logger.info("Dry run mode - no files will be converted")

    # Setup articles directory
    if not dry_run:
        setup_articles_directory()

    success_count = 0
    error_count = 0

    for conversion in CONVERSIONS:
        source = conversion["source"]
        target = conversion["target"]
        description = conversion["description"]

        if not os.path.exists(source):
            logger.warning("Source file not found: %s (%s)", source, description)
            error_count += 1
            continue

        if dry_run:
            logger.info("Would convert: %s -> %s", source, target)
            success_count += 1
        else:
            try:
                converter.convert_file(source, target)
                logger.info("Converted: %s -> %s", source, target)
                success_count += 1
            except Exception as e:
                logger.error("Failed to convert %s: %s", source, e)
                error_count += 1

    if not dry_run and success_count > 0:
        logger.info("Successfully converted %d files", success_count)

    return error_count == 0


def main() -> None:
    """Main entry point."""
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    if "--help" in sys.argv or "-h" in sys.argv:
        sys.exit(0)

    success = convert_all(dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
