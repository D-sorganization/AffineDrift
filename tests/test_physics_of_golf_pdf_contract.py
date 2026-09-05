"""PDF-toolchain contracts for The Physics of Golf Quarto book."""

import re
from pathlib import Path

CONFIG = Path("articles/The_Physics_of_Golf/quarto/_quarto.yml")
FORCES_CHAPTER = Path("articles/The_Physics_of_Golf/quarto/ch04_forces_and_torques.qmd")
TRIPLE_PENDULUM_CHAPTER = Path("articles/The_Physics_of_Golf/quarto/ch08_triple_pendulum.qmd")
PARALLEL_MECHANISMS_CHAPTER = Path(
    "articles/The_Physics_of_Golf/quarto/ch09_parallel_mechanisms.qmd"
)
FLEXIBLE_SHAFT_CHAPTER = Path("articles/The_Physics_of_Golf/quarto/ch11_flexible_shaft.qmd")
FASCIA_CHAPTER = Path("articles/The_Physics_of_Golf/quarto/ch12_fascia.qmd")
SPINE_CHAPTER = Path("articles/The_Physics_of_Golf/quarto/ch21_spine_modeling.qmd")
LATEX_BOOK = Path("articles/The_Physics_of_Golf")


def test_lualatex_bold_math_uses_unicode_math_command() -> None:
    """Keep Unicode Greek symbols out of the legacy ``bm`` package path."""
    text = CONFIG.read_text(encoding="utf-8")

    assert r"\usepackage{bm}" not in text
    assert r"\newcommand{\bm}[1]{\symbf{#1}}" in text
    for macro in (
        "control",
        "massmat",
        "cormat",
        "gravvec",
        "drift",
        "inputmap",
        "constraintforce",
        "shaftdamp",
    ):
        assert rf"\providecommand{{\{macro}}}" in text

    assert r"\renewcommand{\chaptermark}[1]{\markboth{\chaptername\ \thechapter}{}}" in text


def test_bold_prose_does_not_leak_into_bold_math_argument() -> None:
    """Keep Markdown emphasis delimiters outside the LaTeX math group."""
    text = FORCES_CHAPTER.read_text(encoding="utf-8")

    assert r"\bm{\tau**" not in text


def test_christoffel_expression_is_inside_display_math() -> None:
    """Prevent Pandoc from escaping mathematical subscripts as prose."""
    text = TRIPLE_PENDULUM_CHAPTER.read_text(encoding="utf-8")
    expression = r"C_i = \sum_{j, k} \frac{\partial M_{ij}}{\partial q_k} \dot{q}_j \dot{q}_k"

    assert f"$$\n{expression}\n$$" in text

    for expression in (
        r"C_3 \approx \frac{\partial M_{23}}{\partial q_2} \dot{q}_2 \dot{q}_3 + \text{(cross terms)}",
        r"C_3 \approx 0.01 \times 600 = 6 \text{ Nm}",
    ):
        assert f"$$\n{expression}\n$$" in text

    inertia_expression = r"T = \frac{1}{2} I \omega^2 \implies \omega = \sqrt{\frac{2T}{I}}"
    assert f"$$\n{inertia_expression}\n$$" in text


def test_elastic_and_constraint_expressions_are_inside_display_math() -> None:
    """Keep the actual closure and tissue-model equations in math mode."""
    text = PARALLEL_MECHANISMS_CHAPTER.read_text(encoding="utf-8")
    displays = re.findall(r"\$\$(.*?)\$\$", text, flags=re.DOTALL)

    for expression in (
        r"T_L^{-1}T_R=H_L^{-1}H_R",
        r"V_e=\tfrac12k(\Delta-\Delta_0)^2",
    ):
        assert any(expression in display for display in displays)


def test_shaft_stiffness_has_one_grouped_subscript() -> None:
    """Avoid invalid adjacent subscripts in the passive-stiffness symbol."""
    text = FLEXIBLE_SHAFT_CHAPTER.read_text(encoding="utf-8")

    assert r"k_{\text{shaft}}_0" not in text
    assert r"k_{\text{shaft},0}" in text


def test_fascia_energy_estimates_are_inside_display_math() -> None:
    """Keep the two worked energy estimates in math mode."""
    text = FASCIA_CHAPTER.read_text(encoding="utf-8")

    for expression in (
        r"E_{\text{stored}} = \frac{1}{2} E \times \epsilon^2 \times V = \frac{1}{2} \times 1 \, \mathrm{MPa} \times (0.05)^2 \times (0.01 \, \mathrm{m}^2 \times 0.1 \, \mathrm{m})",
        r"E_{\text{stored}} = \frac{1}{2} \times 10^6 \, \mathrm{Pa} \times 0.0025 \times 10^{-3} \, \mathrm{m}^3 = 1.25 \, \mathrm{J}",
    ):
        assert f"$$\n{expression}\n$$" in text


def test_spine_display_equation_has_no_nested_math_delimiters() -> None:
    """Keep the degree symbol inside the surrounding display equation."""
    text = SPINE_CHAPTER.read_text(encoding="utf-8")

    assert r"\times 5$^{\circ}$" not in text
    assert r"\times 5^{\circ}" in text


def test_spinal_ligament_cases_have_a_row_separator() -> None:
    """Keep both alternatives in separate rows of the LaTeX cases array."""
    text = SPINE_CHAPTER.read_text(encoding="utf-8")

    assert (
        r"0, & \text{if } \Delta L < L_{\mathrm{slack}}, \\" + "\n"
        r"k_{\mathrm{ligament}} (L - L_0)^2, & \text{if } L > L_{\mathrm{slack}}."
    ) in text


def test_latex_book_uses_its_declared_counterfactual_macros() -> None:
    """Prevent undefined uppercase counterfactual commands in the PDF build."""
    style = (LATEX_BOOK / "golf_physics.sty").read_text(encoding="utf-8")
    chapters = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted((LATEX_BOOK / "chapters").glob("*.tex"))
    )

    assert r"\newcommand{\ztcf}" in style
    assert r"\newcommand{\zvcf}" in style
    assert r"\ZTCF" not in chapters
    assert r"\ZVCF" not in chapters
