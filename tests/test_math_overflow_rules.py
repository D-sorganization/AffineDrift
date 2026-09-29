"""Regression test for the consolidated display-math overflow rule (issue #4581).

Display-math overflow (``.math.display``, ``.MathJax_Display`` and
``mjx-container[display="true"]``) used to be defined independently in
``custom.scss`` *and* in two separate, conflicting blocks inside
``styles.css`` — with different ``overflow-y``, ``padding`` and mobile
``font-size`` values depending on which rule the cascade happened to apply
last. This locks the consolidation down to a single canonical rule set
(a base rule plus its two responsive breakpoints) so the duplication cannot
silently return.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

_RULE_RE = re.compile(r"([^{}]*)\{([^{}]*)\}")


def _read(name: str) -> str:
    return (REPO_ROOT / name).read_text(encoding="utf-8")


def _iter_rules(css: str):
    """Yield (selector, body) for every leaf (non-nested) rule in ``css``.

    Repeatedly matches and strips the innermost ``{...}`` pairs so rules
    nested inside ``@media`` blocks are found the same as top-level rules,
    without needing a full CSS parser.
    """
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    while True:
        match = _RULE_RE.search(css)
        if not match:
            return
        selector, body = match.group(1).strip(), match.group(2).strip()
        if selector and not selector.startswith("@"):
            yield selector, body
        css = css[: match.start()] + " " + css[match.end() :]


def _targets_math_display(selector: str) -> bool:
    """True if one of the selector's comma-separated parts *is* `.math.display`
    (or an equivalent MathJax display-math container), as opposed to merely
    scoping some ancestor selector onto it (e.g. `.main-content-area .math.display`,
    which is an unrelated prose-width constraint, not part of the overflow rule)."""
    parts = {part.strip() for part in selector.split(",")}
    return bool(
        parts
        & {
            ".math.display",
            ".MathJax_Display",
            'mjx-container[display="true"]',
            'mjx-container[jax="CHTML"][display="true"]',
        }
    )


def _math_display_overflow_rules(css: str) -> list[tuple[str, str]]:
    """Rules touching `.math.display`'s box model, excluding scrollbar cosmetics."""
    return [
        (selector, body)
        for selector, body in _iter_rules(css)
        if _targets_math_display(selector) and "webkit-scrollbar" not in selector
    ]


class TestNoDuplicateMathOverflowRules:
    def test_custom_scss_defines_no_math_overflow_rule(self):
        """The duplicate rule set must be removed from custom.scss entirely.

        Explanatory comments may still *mention* the relocated selectors, so
        comments are stripped before checking for a live rule/selector.
        """
        scss = _read("custom.scss")
        assert _math_display_overflow_rules(scss) == []
        code_only = re.sub(r"/\*.*?\*/", "", scss, flags=re.DOTALL)
        assert "MathJax_Display" not in code_only
        assert "mjx-container" not in code_only

    def test_styles_css_has_exactly_one_rule_set(self):
        """Exactly one base rule plus its two responsive breakpoints remain.

        Before the fix, styles.css alone had two independent base rules (plus
        their own breakpoints), on top of the duplicate in custom.scss — six
        overlapping rules in total defining conflicting overflow-y/padding/
        font-size values for the same elements.
        """
        css = _read("styles.css")
        rules = _math_display_overflow_rules(css)
        assert len(rules) == 3, f"expected 1 base rule + 2 breakpoints, got: {rules}"

    def test_consolidated_rule_preserves_effective_computed_values(self):
        """The merged rule must reproduce exactly what the old cascade rendered.

        These values are the *result* of resolving the previous conflicting
        declarations (later rule wins for equal specificity), not an
        arbitrary choice — changing any of them would move the 390px mobile
        math snapshots.
        """
        css = _read("styles.css")
        bodies = " ".join(body for _, body in _math_display_overflow_rules(css))
        assert "overflow-x: auto" in bodies
        assert "overflow-y: hidden" in bodies
        assert "overflow-y: visible" not in bodies
        assert "display: block" in bodies
        assert "max-width: 100%" in bodies
        assert "margin-bottom: 1rem" in bodies
        assert "scroll-behavior: smooth" in bodies
        assert "scrollbar-width: thin" in bodies
        assert "-webkit-overflow-scrolling: touch" in bodies
        assert "font-size: 0.9em !important" in bodies
        assert "font-size: 0.85em !important" in bodies
