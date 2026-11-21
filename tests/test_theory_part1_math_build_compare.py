"""#5253: Theory Part 1 math build comparison script."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.theory_part1_math_build_compare import (
    KATEX_METADATA,
    build_comparison_payload,
    compare_theory_part1_math_build,
    main,
)


class TestTheoryPart1MathBuildCompare(unittest.TestCase):
    """Quarto build comparison contract."""

    def test_build_comparison_payload_includes_profile_labels(self) -> None:
        payload = build_comparison_payload(
            {"mathjax_gate": 12.0, "katex_prototype": 11.0, "delta_seconds": -1.0}
        )
        self.assertEqual(payload["katex_metadata_override"], KATEX_METADATA)
        self.assertIn("not server-side", str(payload["note"]))

    def test_katex_override_uses_quarto_colon_metadata(self) -> None:
        """Quarto -M overrides use KEY:VALUE (colons), not equals signs."""
        self.assertEqual(KATEX_METADATA, "html-math-method:katex")
        self.assertNotIn("=", KATEX_METADATA)

    @patch("scripts.theory_part1_math_build_compare.subprocess.run")
    def test_render_once_passes_katex_metadata_to_quarto(self, run_mock: object) -> None:
        from scripts.theory_part1_math_build_compare import _render_once

        run_mock.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="",
            stderr="",
        )
        _render_once(KATEX_METADATA, Path("/tmp/out-katex-5253"))
        command = run_mock.call_args[0][0]
        self.assertIn("-M", command)
        katex_index = command.index("-M") + 1
        self.assertEqual(command[katex_index], KATEX_METADATA)

    @patch("scripts.theory_part1_math_build_compare._render_once", side_effect=[10.0, 9.5])
    @patch("scripts.theory_part1_math_build_compare._quarto_available", return_value=True)
    def test_compare_invokes_two_renders(
        self,
        _quarto: object,
        render_mock: object,
    ) -> None:
        timings = compare_theory_part1_math_build(work_root=Path("/tmp/compare-5253"))
        self.assertAlmostEqual(timings["delta_seconds"], -0.5)
        self.assertEqual(render_mock.call_count, 2)

    def test_main_dry_run_emits_json(self) -> None:
        exit_code = main(["--dry-run"])
        self.assertEqual(exit_code, 0)

    @patch("scripts.theory_part1_math_build_compare.subprocess.run")
    def test_render_once_raises_on_quarto_failure(self, run_mock: object) -> None:
        from scripts.theory_part1_math_build_compare import _render_once

        run_mock.return_value = subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout="",
            stderr="boom",
        )
        with self.assertRaises(RuntimeError):
            _render_once(None, Path("/tmp/out-5253"))


if __name__ == "__main__":
    unittest.main()
