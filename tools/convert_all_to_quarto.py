#!/usr/bin/env python3
"""
Batch LaTeX to Quarto Converter for AffineDrift
Converts all LaTeX article files to Quarto .qmd format
"""

import os
import sys

from latex_to_qmd import LaTeXToQuartoConverter

# Articles directory for Quarto documents
ARTICLES_DIR = "articles"

# Mapping of LaTeX files to their Quarto output locations
CONVERSIONS = [
    # Already converted - keeping for reference
    {
        "source": "content/Wrist as Universal Joint/Wrist_Universal_Claude.tex",
        "target": f"{ARTICLES_DIR}/wrist-universal-joint.qmd",
        "description": "Wrist as Universal Joint article"
    },
    {
        "source": "content/Inverse Dynamics Analysis/Drafts/Inverse Dynamics Claude Current/inverse_dynamics_final.tex",
        "target": f"{ARTICLES_DIR}/inverse-dynamics.qmd",
        "description": "Inverse Dynamics article"
    },
    # Affine Background Articles
    {
        "source": "content/Affine Background Articles/Nonlinear_Control_Insights.tex",
        "target": f"{ARTICLES_DIR}/nonlinear-control-insights.qmd",
        "description": "Nonlinear Control Theory Insights"
    },
    {
        "source": "content/Affine Background Articles/Force_Mobility_Matrices.tex",
        "target": f"{ARTICLES_DIR}/force-mobility-matrices.qmd",
        "description": "Force Mobility Matrices"
    },
    {
        "source": "content/Affine Background Articles/Inverse_Dynamics_Inference.tex",
        "target": f"{ARTICLES_DIR}/inverse-dynamics-inference.qmd",
        "description": "Inverse Dynamics Inference"
    },
    {
        "source": "content/Affine Background Articles/Lagrangian_Reference.tex",
        "target": f"{ARTICLES_DIR}/lagrangian-reference.qmd",
        "description": "Lagrangian Reference"
    },
    {
        "source": "content/Affine Background Articles/ScrewTheory_Reference.tex",
        "target": f"{ARTICLES_DIR}/screw-theory-reference.qmd",
        "description": "Screw Theory Reference"
    },
    {
        "source": "content/Affine Background Articles/null_space_constraint_jacobian.tex",
        "target": f"{ARTICLES_DIR}/null-space-constraint-jacobian.qmd",
        "description": "Null Space Constraint Jacobian"
    },
    # Affine Nature of the Golf Swing
    {
        "source": "content/Affine Nature of the Golf Swing/Draft3_Compiled_Working_Copy.tex",
        "target": f"{ARTICLES_DIR}/affine-nature-golf-swing.qmd",
        "description": "Affine Nature of the Golf Swing (Main Article)"
    },
    {
        "source": "content/Affine Nature of the Golf Swing/Appendix_A_Nonlinear_Control_Insights.tex",
        "target": f"{ARTICLES_DIR}/appendix-nonlinear-control-insights.qmd",
        "description": "Appendix A: Nonlinear Control Insights"
    },
    {
        "source": "content/Affine Nature of the Golf Swing/Appendix_B_Inverse_Dynamics_Inference.tex",
        "target": f"{ARTICLES_DIR}/appendix-inverse-dynamics-inference.qmd",
        "description": "Appendix B: Inverse Dynamics Inference"
    },
    {
        "source": "content/Affine Nature of the Golf Swing/Appendix_C_Applications.tex",
        "target": f"{ARTICLES_DIR}/appendix-applications.qmd",
        "description": "Appendix C: Applications"
    },
    {
        "source": "content/Affine Nature of the Golf Swing/Appendix_D_Lagrangian_Reference.tex",
        "target": f"{ARTICLES_DIR}/appendix-lagrangian-reference.qmd",
        "description": "Appendix D: Lagrangian Reference"
    },
    {
        "source": "content/Affine Nature of the Golf Swing/Appendix_E_ScrewTheory_Reference.tex",
        "target": f"{ARTICLES_DIR}/appendix-screw-theory-reference.qmd",
        "description": "Appendix E: Screw Theory Reference"
    },
]


def setup_articles_directory():
    """Create articles directory if it doesn't exist"""
    os.makedirs(ARTICLES_DIR, exist_ok=True)

    # Create _metadata.yml for articles
    metadata_path = os.path.join(ARTICLES_DIR, "_metadata.yml")
    if not os.path.exists(metadata_path):
        with open(metadata_path, 'w') as f:
            f.write("""# Shared metadata for all articles
format:
  html:
    toc: true
    toc-depth: 3
    number-sections: false
    code-fold: true
    css: ../styles.css
""")
        print(f"✓ Created {metadata_path}")


def convert_all(dry_run=False):
    """Convert all LaTeX files to Quarto"""
    converter = LaTeXToQuartoConverter()

    print("=" * 70)
    print("AffineDrift LaTeX to Quarto Batch Converter")
    print("=" * 70)
    print()

    if dry_run:
        print("DRY RUN MODE - No files will be modified")
        print()

    # Setup articles directory
    if not dry_run:
        setup_articles_directory()
        print()

    success_count = 0
    error_count = 0

    for conversion in CONVERSIONS:
        source = conversion["source"]
        target = conversion["target"]
        description = conversion["description"]

        print(f"Processing: {description}")
        print(f"  Source: {source}")
        print(f"  Target: {target}")

        if not os.path.exists(source):
            print(f"  ✗ Source file not found: {source}")
            error_count += 1
            continue

        if dry_run:
            print("  ✓ Would convert (dry run)")
            success_count += 1
        else:
            try:
                converter.convert_file(source, target)
                success_count += 1
            except Exception as e:
                print(f"  ✗ Error converting: {e}")
                error_count += 1

        print()

    print("=" * 70)
    print("Conversion Summary:")
    print(f"  Successful: {success_count}")
    print(f"  Errors: {error_count}")
    print("=" * 70)

    if not dry_run and success_count > 0:
        print()
        print("Next steps:")
        print("  1. Install Quarto: https://quarto.org/docs/get-started/")
        print("  2. Preview site: quarto preview")
        print("  3. Render site: quarto render")
        print("  4. Publish: quarto publish gh-pages")

    return error_count == 0


def main():
    """Main entry point"""
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python3 convert_all_to_quarto.py [--dry-run|-n] [--help|-h]")
        print()
        print("Options:")
        print("  --dry-run, -n  : Preview what would be converted without making changes")
        print("  --help, -h     : Show this help message")
        sys.exit(0)

    success = convert_all(dry_run)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
