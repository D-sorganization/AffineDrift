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


def _iter_rules_with_media(css: str):
    """Yield (media_query_or_None, selector, body) for every leaf rule.

    Unlike `_iter_rules`, this keeps track of which `@media` block (if any)
    encloses each rule, so callers can tell a base-level declaration apart
    from its responsive breakpoint override for the *same* selector.
    """
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    media_stack: list[str] = []
    header_start = 0
    i = 0
    while i < len(css):
        char = css[i]
        if char == "{":
            header = css[header_start:i].strip()
            if header.startswith("@"):
                media_stack.append(header)
                header_start = i + 1
            else:
                close = css.index("}", i)
                body = css[i + 1 : close].strip()
                if header:
                    yield (media_stack[-1] if media_stack else None), header, body
                i = close
                header_start = i + 1
        elif char == "}":
            if media_stack:
                media_stack.pop()
            header_start = i + 1
        i += 1


def _bodies_for_selector(css: str, selector_token: str, *, media_contains: str | None) -> list[str]:
    """Bodies of rules whose selector list contains exactly `selector_token`.

    `media_contains` selects the scope: `None` for base (non-media) rules, or
    a substring like `"768px"` to scope to that breakpoint's `@media` block.
    """
    out = []
    for media, selector, body in _iter_rules_with_media(css):
        if "webkit-scrollbar" in selector:
            continue
        parts = {part.strip() for part in selector.split(",")}
        if selector_token not in parts:
            continue
        if media_contains is None:
            if media is not None:
                continue
        else:
            if media is None or media_contains not in media:
                continue
        out.append(body)
    return out


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
        """One shared rule set plus one `.math.display`-only rule, per breakpoint.

        Before the *first* fix, styles.css alone had two independent base
        rules (plus their own breakpoints), on top of the duplicate in
        custom.scss — six overlapping rules in total defining conflicting
        overflow-y/padding/font-size values for the same elements.

        The shared rule (`mjx-container[jax="CHTML"][display="true"]`,
        `.MathJax_Display`, `.math.display`) carries the overflow/scrollbar
        declarations common to all three. `padding-top` and `scroll-behavior`
        must stay on a `.math.display`-only rule instead of joining the
        shared one, because MathJax renders `mjx-container` *inside*
        `span.math.display` — giving both elements the same top padding
        doubles the visible gap above every display equation. That is one
        shared rule + one `.math.display`-only rule, per scope (base + 2
        breakpoints) = 6 rules.
        """
        css = _read("styles.css")
        rules = _math_display_overflow_rules(css)
        assert len(rules) == 6, (
            f"expected 3 shared rules (base + 2 breakpoints) plus 3 "
            f".math.display-only rules (base + 2 breakpoints), got: {rules}"
        )

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

    def test_padding_top_and_scroll_behavior_are_scoped_to_math_display_only(self):
        """`padding-top`/`scroll-behavior` must apply to `.math.display` alone.

        Before the PR (origin/main), only the bare `.math.display` wrapper
        span carried `padding-top`/`scroll-behavior` — MathJax's own
        `mjx-container`/`.MathJax_Display` never did. The consolidation must
        preserve that split rather than folding all three selectors into one
        rule, or `mjx-container` (rendered *inside* `span.math.display`)
        picks up a second `padding-top` and every display equation gets a
        doubled top gap, moving the 390px mobile math snapshots.
        """
        css = _read("styles.css")

        math_display_base = " ".join(
            _bodies_for_selector(css, ".math.display", media_contains=None)
        )
        assert "padding-top: 1rem" in math_display_base
        assert "scroll-behavior: smooth" in math_display_base

        mobile_padding = {"768px": "0.75rem", "480px": "0.5rem"}
        for breakpoint, expected in mobile_padding.items():
            mobile_body = " ".join(
                _bodies_for_selector(css, ".math.display", media_contains=breakpoint)
            )
            assert f"padding-top: {expected}" in mobile_body, (
                f"expected .math.display padding-top: {expected} at {breakpoint}, "
                f"got: {mobile_body}"
            )

        for other_selector in (".MathJax_Display", 'mjx-container[jax="CHTML"][display="true"]'):
            other_base = " ".join(_bodies_for_selector(css, other_selector, media_contains=None))
            assert "padding-top" not in other_base, (
                f"{other_selector} must not get padding-top (doubles the top gap "
                f"MathJax already gets from its `.math.display` wrapper): {other_base}"
            )
            assert (
                "scroll-behavior" not in other_base
            ), f"{other_selector} must not get scroll-behavior: {other_base}"
            for breakpoint in mobile_padding:
                other_mobile = " ".join(
                    _bodies_for_selector(css, other_selector, media_contains=breakpoint)
                )
                assert (
                    "padding-top" not in other_mobile
                ), f"{other_selector} must not get padding-top at {breakpoint}: {other_mobile}"
