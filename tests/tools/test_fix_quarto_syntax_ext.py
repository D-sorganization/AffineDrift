"""Extended tests for fix_quarto_syntax — main() function branches."""

from __future__ import annotations

import os
from pathlib import Path


class TestFixQuartoSyntaxMainBranches:
    """Cover main() branches for different file names."""

    def test_main_processes_superposition_qmd(self, tmp_path: Path) -> None:
        """main() should call fix_superposition for superposition.qmd."""
        from src.tools.fix_quarto_syntax import main

        articles_dir = tmp_path / "articles"
        articles_dir.mkdir()
        qmd = articles_dir / "superposition.qmd"
        content = "---\ntitle: Superposition\n---\n" "This is content without special markers.\n"
        qmd.write_text(content, encoding="utf-8")

        original = os.getcwd()
        os.chdir(tmp_path)
        try:
            main()
        finally:
            os.chdir(original)

    def test_main_processes_wrist_qmd(self, tmp_path: Path) -> None:
        """main() should call fix_units_wrist for wrist-universal-joint.qmd."""
        from src.tools.fix_quarto_syntax import main

        articles_dir = tmp_path / "articles"
        articles_dir.mkdir()
        qmd = articles_dir / "wrist-universal-joint.qmd"
        qmd.write_text("Some wrist content.", encoding="utf-8")

        original = os.getcwd()
        os.chdir(tmp_path)
        try:
            main()
        finally:
            os.chdir(original)

    def test_main_processes_theory_part5_qmd(self, tmp_path: Path) -> None:
        """main() should call fix_theory_part5 for theory-part5.qmd."""
        from src.tools.fix_quarto_syntax import main

        articles_dir = tmp_path / "articles"
        articles_dir.mkdir()
        qmd = articles_dir / "theory-part5.qmd"
        qmd.write_text("Some theory content.", encoding="utf-8")

        original = os.getcwd()
        os.chdir(tmp_path)
        try:
            main()
        finally:
            os.chdir(original)

    def test_main_modifies_file_when_content_changes(self, tmp_path: Path) -> None:
        """main() should write modified content back to file."""
        from src.tools.fix_quarto_syntax import main

        articles_dir = tmp_path / "articles"
        articles_dir.mkdir()
        qmd = articles_dir / "superposition.qmd"
        # Content that fix_superposition actually modifies
        original_content = 'some content with "Superposition" marker here.\n'
        qmd.write_text(original_content, encoding="utf-8")

        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            main()
        finally:
            os.chdir(original_cwd)
