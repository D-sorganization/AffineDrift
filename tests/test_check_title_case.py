"""Tests for the website title-case gate."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_title_case import expected_title, findings_for_text


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("Book series", "Book Series"),
        ("why torque matters", "Why Torque Matters"),
        ("An introduction to control-affine systems", "An Introduction to Control-Affine Systems"),
        ("Motion capture: from markers to models", "Motion Capture: From Markers to Models"),
        ("The Physics of Golf", "The Physics of Golf"),
        ("DCR and ZTCF in MuJoCo", "DCR and ZTCF in MuJoCo"),
        ("Volume II: Control Is Motion", "Volume II: Control Is Motion"),
        ("Defense (The Effective Plant Fallacy)", "Defense (The Effective Plant Fallacy)"),
        (r"A.1 \quad coupled equations", r"A.1 \quad Coupled Equations"),
        ("Mechanical vs. control causality", "Mechanical vs. Control Causality"),
        ("Numerical Fréchet derivative", "Numerical Fréchet Derivative"),
        ("Numerical example: van der Pol oscillator", "Numerical Example: van der Pol Oscillator"),
        ("Expansion of $f(x)$", "Expansion of $f(x)$"),
        ("Docking: 1 km to 10 m approach", "Docking: 1 km to 10 m Approach"),
        ("Setting up the equations", "Setting Up the Equations"),
        ("State-of-the-art control", "State-of-the-Art Control"),
        ("What can we determine? the subspace", "What Can We Determine? The Subspace"),
        ("See @sec-control: the result", "See @sec-control: The Result"),
        ("The FréChet derivative on so(3)", "The Fréchet Derivative on SO(3)"),
        (r"Moving Poincar\'E sections", r"Moving Poincar\'e Sections"),
        ("Jump in δX", "Jump in δx"),
        ("Why so(3) matters", "Why SO(3) Matters"),
        (
            "Read Tangent_Hyperplanes_Unified_Thesis.Qmd",
            "Read Tangent_Hyperplanes_Unified_Thesis.qmd",
        ),
        ("state‐of‐the‐art control", "State‐of‐the‐Art Control"),
    ],
)
def test_expected_title_uses_title_case(source: str, expected: str) -> None:
    assert expected_title(source) == expected


def test_finds_visible_page_titles_and_chart_titles() -> None:
    text = """---
title: "A guide to drift"
---

## why affine systems matter

```{python}
ax.set_title("energy over time")
```

::: {#fig-demo}
Demo
:::

![A trajectory](trajectory.png){#fig-trajectory fig-cap="motion through state space"}
"""

    findings = findings_for_text(Path("article.qmd"), text)

    assert [(finding.kind, finding.actual, finding.expected) for finding in findings] == [
        ("page title", "A guide to drift", "A Guide to Drift"),
        ("heading", "why affine systems matter", "Why Affine Systems Matter"),
        ("chart title", "energy over time", "Energy Over Time"),
        ("figure caption", "motion through state space", "Motion Through State Space"),
    ]


def test_ignores_prose_and_non_title_code() -> None:
    text = """---
title: "A Guide to Drift"
---

This sentence is deliberately sentence case.

```{python}
description = "not a title"
```
"""

    assert findings_for_text(Path("article.qmd"), text) == []


def test_finds_f_string_chart_titles() -> None:
    text = """```{python}
plt.title(f"residual grows as O(t²)")
```"""

    findings = findings_for_text(Path("article.qmd"), text)

    assert [(finding.actual, finding.expected) for finding in findings] == [
        ("residual grows as O(t²)", "Residual Grows as O(t²)"),
    ]


def test_finds_chart_titles_in_python_modules() -> None:
    text = """def draw(ax, angle):
    ax.set_title(
        "torque over time "
        f"(Angle: {angle:.0f}°)"
    )
"""

    findings = findings_for_text(Path("src/plot.py"), text)

    assert [(finding.actual, finding.expected) for finding in findings] == [
        ("torque over time (Angle:", "Torque Over Time (Angle:"),
    ]


def test_quarto_navigation_labels_are_checked() -> None:
    text = """website:
  sidebar:
    - section: "Book series volumes"
  navbar:
    - text: "Learning paths"
"""

    findings = findings_for_text(Path("_quarto.yml"), text)

    assert [(finding.kind, finding.expected) for finding in findings] == [
        ("navigation label", "Book Series Volumes"),
        ("navigation label", "Learning Paths"),
    ]
