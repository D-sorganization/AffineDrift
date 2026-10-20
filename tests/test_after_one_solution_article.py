"""Contract tests for the article "After One Solution" (#5096).

The article ``articles/after-one-solution-null-space-exploration.qmd`` states propositions
P1-P7 and quotes numbers produced by the companion code of #5094 (linear propositions) and #5095
(nonlinear continuation).  These tests pin four things so the prose cannot drift from the code:

1. every quoted number equals the value in ``data/null_space_exploration/examples.json``;
2. the eleven sections, propositions P1-P7 (hypotheses, conclusion, proof) and the binding
   mathematical qualifications are present, and the forbidden claims are absent;
3. cross-links (in-page anchors, links to other articles, bibliography keys, companion names)
   resolve;
4. the small loader that the article's code listing imports honours its contract.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

from src.tools import null_space_continuation_examples as continuation_module
from src.tools import null_space_exploration_examples as linear_module
from src.tools.null_space_article_data import example_section, load_examples
from src.tools.utils.frontmatter import split_frontmatter
from src.tools.utils.frontmatter_schema import validate_article_frontmatter

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "articles/after-one-solution-null-space-exploration.qmd"
ARTICLE_REL = "articles/after-one-solution-null-space-exploration.qmd"
EXAMPLES = ROOT / "data/null_space_exploration/examples.json"
NEW_BIB = ROOT / "references/null-space-exploration.bib"
INCLUDE = "{{< include ../_includes/induced-acceleration-attribution-contract.qmd >}}"
TITLE = "After One Solution: Exploring Dynamically Equivalent Force Allocations"

SECTION_IDS = [
    "sec-setting",
    "sec-fibre",
    "sec-metrics",
    "sec-constraints",
    "sec-optimizing",
    "sec-exploring",
    "sec-identifiable",
    "sec-time",
    "sec-nonlinear",
    "sec-buys-the-rest",
    "sec-upstreamdrift",
]
PR_NUMBERS = ("13475", "13470", "13467", "13493")
NEGLIGIBLE = 1e-9  # LP and rounding noise in examples.json that the article quotes as zero.
FENCE = re.compile(r"^\s*(```+|~~~+)")


# ------------------------------------------------------------------------- formatting rules


def clean(value: float) -> float:
    """Round solver noise (``6.7e-16``) to zero and normalise negative zero."""
    rounded = round(float(value), 9)
    return 0.0 if rounded == 0.0 else rounded


def tex(value: float, digits: int = 4) -> str:
    """Number as the article prints it: ``digits`` significant digits, LaTeX exponents."""
    number = float(value)
    if number == 0.0:
        return "0"
    if 1e-3 <= abs(number) < 1e4:
        return f"{number:.{digits}g}"
    mantissa, exponent = f"{number:.{digits - 1}e}".split("e")
    shown = f"{float(mantissa):.{digits}g}"
    power = f"10^{{{int(exponent)}}}"
    if shown == "1":
        return power
    return f"{shown}\\times{power}"


def vec(values: list[float]) -> str:
    """``(a,\\,b)`` vector as written in the article."""
    return "(" + ",\\,".join(tex(clean(v)) for v in values) + ")"


def span(values: list[float]) -> str:
    """``[a,\\,b]`` interval as written in the article."""
    return "[" + ",\\,".join(tex(clean(v)) for v in values) + "]"


def mat(rows: list[list[float]]) -> str:
    """``bmatrix`` as written in the article."""
    body = "\\\\".join("&".join(tex(clean(v)) for v in row) for row in rows)
    return "\\begin{bmatrix}" + body + "\\end{bmatrix}"


# --------------------------------------------------------------------------------- fixtures


def _text() -> str:
    return ARTICLE.read_text(encoding="utf-8")


def _body_lines() -> list[tuple[int, str]]:
    """(number, line) outside fenced code."""
    inside, out = False, []
    for number, line in enumerate(_text().splitlines(), 1):
        if FENCE.match(line):
            inside = not inside
            continue
        if not inside:
            out.append((number, line))
    return out


type Tokens = list[tuple[str, str]]


def _p1_to_p3_tokens(linear: dict[str, Any]) -> Tokens:
    p1, p2, p3 = linear["p1"], linear["p2"], linear["p3"]
    weights = p2["weight_diagonal"]
    tokens: Tokens = [
        ("p1 survey", f"| {r['m']} | {r['n']} | {r['rank']} | {r['nullity']} |")
        for r in p1["survey"]
    ]
    tokens += [
        ("p1 empty residual", rf"\rho_{{\mathrm{{LS}}}}={tex(p1['empty']['residual'])}"),
        ("p2 weight", rf"\operatorname{{diag}}({tex(weights[0])},\,{tex(weights[1])})"),
        ("p2 weighted", vec(p2["u_weighted"])),
        ("p2 euclidean", vec(p2["u_euclidean"])),
        ("p2 rescaled", vec(p2["u_rescaled_half"])),
        ("p2 projector", mat(p2["projector"])),
        ("p3 reduced hessian", mat(p3["reduced_hessian"])),
        ("p3 u_star", vec(p3["u_star"])),
        ("p3 u_kkt", vec(p3["u_kkt"])),
    ]
    return tokens


def _p4_to_p7_tokens(linear: dict[str, Any]) -> Tokens:
    p4, p5, p7 = linear["p4"], linear["p5"], linear["p7"]
    tokens: Tokens = [
        ("p4 split", span(p4["split_interval"])),
        ("p4 net", span(p4["net_interval"])),
        ("p4 residual", rf"\rho={tex(p4['split_residual'])}"),
        ("p5 epsilon", rf"\varepsilon={tex(p5['epsilon'])}"),
        ("p7 delta", rf"\delta={tex(p7['delta'])}"),
    ]
    tokens += [
        ("p5 row", f"| ${tex(r['step'])}$ | ${tex(r['actual'])}$ | ${tex(r['bound'])}$ |")
        for r in p5["steps"]
    ]
    tokens += [(f"p7 {key}", span(item)) for key in ("framewise", "coupled") for item in p7[key]]
    return tokens


def _toy_tokens(linear: dict[str, Any]) -> Tokens:
    muscle, grip = linear["three_muscle"], linear["planar_grip"]
    keys = (
        "muscle_1_interval",
        "muscle_3_interval",
        "muscle_1_disabled_interval",
        "muscle_3_disabled_interval",
    )
    tokens: Tokens = [("muscle A", mat(muscle["A"])), ("muscle b", vec(muscle["b"]))]
    tokens += [(f"muscle {key}", span(muscle[key])) for key in keys]
    return tokens + [
        ("grip friction", rf"\mu={tex(linear_module.FRICTION_COEFFICIENT)}"),
        ("grip span", rf"{tex(linear_module.GRIP_HALF_SPAN_M)}\,\mathrm{{m}}"),
        ("grip load", rf"{tex(linear_module.GRIP_LOAD_N)}\,\mathrm{{N}}"),
        ("grip net wrench", vec(grip["net_wrench"])),
        ("grip squeeze", span(grip["lead_squeeze_interval"])),
        ("grip vertical", span(grip["lead_vertical_interval"])),
    ]


def _residual_row(step: float, circle: float, fold: float) -> str:
    cells = (tex(value, digits=5) for value in (step, circle, fold))
    return "| " + " | ".join(f"${cell}$" for cell in cells) + " |"


def _residual_tokens(cont: dict[str, Any]) -> Tokens:
    residual, corrector = cont["tangent_residual"], cont["corrector_convergence"]
    rows = zip(
        residual["circle"]["steps"],
        residual["circle"]["residuals"],
        residual["fold"]["residuals"],
        strict=True,
    )
    tokens: Tokens = [("tangent residual row", _residual_row(h, c, f)) for h, c, f in rows]
    for name in ("circle", "fold"):
        slope = tex(residual[name]["fitted_slope"])
        tokens.append((f"slope {name}", rf"\hat p_{{\mathrm{{{name}}}}}={slope}"))
    tokens.append(("corrector iterations", f"{corrector['iterations']} corrector iterations"))
    tokens += [("corrector history", f"${tex(v)}$") for v in corrector["residual_history"]]
    return tokens + [("corrector ratio", tex(v)) for v in corrector["ratios"]]


def _continuation_tokens(cont: dict[str, Any]) -> Tokens:
    trace, counter, drop = (
        cont["fold_trace"],
        cont["nearest_point_counterexample"],
        cont["rank_drop"],
    )
    return _residual_tokens(cont) + [
        ("fold min u2", tex(trace["min_u2"])),
        ("fold manifold error", tex(trace["max_manifold_error"])),
        ("fold steps", f"{len(trace['points']) - 1} steps"),
        ("counter start", vec(counter["start"])),
        ("counter gn point", vec(counter["gauss_newton_point"])),
        ("counter gn distance", rf"d_{{\mathrm{{GN}}}}={tex(counter['gauss_newton_distance'])}"),
        ("counter nearest", vec(counter["nearest_point"])),
        ("counter nearest distance", rf"d_\star={tex(counter['nearest_distance'])}"),
        ("rank drop rank", rf"\operatorname{{rank}}DF(0)={drop['jacobian_rank_at_origin']}"),
        ("rank drop kernel", rf"\dim\ker DF(0)={drop['tangent_dimension_at_origin']}"),
    ]


def _quoted_tokens() -> Tokens:
    """(label, exact token) for every number the article quotes from examples.json."""
    linear, cont = example_section("linear"), example_section("continuation")
    return (
        _p1_to_p3_tokens(linear)
        + _p4_to_p7_tokens(linear)
        + _toy_tokens(linear)
        + _continuation_tokens(cont)
    )


QUOTED = _quoted_tokens() if EXAMPLES.exists() else []


# ----------------------------------------------------------------------- 1. quoted numbers


def test_examples_json_is_the_only_number_source() -> None:
    """The loader reads the same file the builder writes."""
    assert load_examples() == json.loads(EXAMPLES.read_text(encoding="utf-8"))


@pytest.mark.parametrize(("label", "token"), QUOTED, ids=[f"{n}:{t[:30]}" for n, t in QUOTED])
def test_quoted_number_matches_examples_json(label: str, token: str) -> None:
    assert token in _text(), f"{label}: {token!r} not found in the article"


def test_booleans_the_article_relies_on_hold_in_the_json() -> None:
    linear, cont = example_section("linear"), example_section("continuation")
    assert linear["three_muscle"]["net_invariant"] is True
    assert linear["planar_grip"]["net_wrench_invariant"] is True
    assert linear["planar_grip"]["lead_squeeze_invariant"] is False
    assert linear["p4"]["split_unbounded_without_limits"] is True
    assert linear["p7"]["contained"] is True
    assert cont["rank_drop"]["detected"] is True
    assert all(row["consistent"] for row in linear["p1"]["survey"])
    assert not linear["p1"]["empty"]["consistent"]
    assert abs(linear["three_muscle"]["muscle_3_disabled_interval"][1]) < NEGLIGIBLE
    assert linear["three_muscle"]["nullity"] == 1


# --------------------------------------------------------------- 2. structure and mathematics


def test_front_matter_conforms_to_the_article_schema() -> None:
    front, _ = split_frontmatter(_text())
    assert validate_article_frontmatter(front, ARTICLE_REL) == []
    assert front["title"] == TITLE
    assert front["canonical"] == "/articles/after-one-solution-null-space-exploration.html"
    bibliographies = front["bibliography"]
    bibliographies = [bibliographies] if isinstance(bibliographies, str) else bibliographies
    assert "../references/null-space-exploration.bib" in bibliographies
    assert any("5096" in str(change) for change in front["changes"])


def test_eleven_sections_appear_in_order() -> None:
    ids = [
        match.group(1)
        for _, line in _body_lines()
        if (match := re.match(r"^## .+\{#(sec-[a-z-]+)\}\s*$", line))
    ]
    assert ids == SECTION_IDS


def test_sections_are_numbered_and_listed_resources_are_unnumbered() -> None:
    front, _ = split_frontmatter(_text())
    assert front["format"]["html"]["number-sections"] is True
    text = _text()
    assert re.search(r"^## References \{\.unnumbered\}", text, re.MULTILINE)
    assert re.search(r"^## Related Articles \{\.unnumbered\}", text, re.MULTILINE)
    assert "::: {#refs}" in text


def _proposition_block(index: int) -> str:
    lines = _text().splitlines()
    start = next(i for i, line in enumerate(lines) if f"{{#prop-p{index}" in line)
    end = next(i for i in range(start + 1, len(lines)) if lines[i].strip() == ":::")
    return "\n".join(lines[start : end + 1])


@pytest.mark.parametrize("index", range(1, 8))
def test_proposition_has_hypotheses_conclusion_and_proof(index: int) -> None:
    block = _proposition_block(index)
    assert f"Proposition P{index}" in block
    assert "**Hypotheses.**" in block
    assert "**Conclusion.**" in block
    text = _text()
    start = text.index(f"{{#prop-p{index}")
    proof = text.find("*Proof.*", start)
    assert proof != -1, f"P{index} has no proof"
    following = text.find("{#prop-p", start + 1)
    assert (
        following == -1 or proof < following
    ), f"P{index}: proof must precede the next proposition"


def test_proposition_p4_covers_invariance_and_enclosing_radius_bound() -> None:
    block = _proposition_block(4)
    for needle in ("range}(A^\\top)", "enclosing", "\\|N^\\top c\\|"):
        assert needle in block, needle


BINDING_PATTERNS = {
    "numerical versus exact invariance": r"numerically invariant at a declared tolerance",
    "exact theorem named": r"exact invariance",
    "enclosing radius": r"enclosing radius",
    "not the inscribed radius": r"(Chebyshev[^.]*inscribed|inscribed[^.]*Chebyshev)",
    "declared polygonal cone": r"declared polygonal",
    "outer approximation": r"outer approximation",
    "inner approximation": r"inner approximation",
    "relative interior start": r"relative interior",
    "true affine hull": r"affine hull",
    "sufficient not necessary": r"sufficient[^.]*not necessary",
    "scale carried once": r"already carries[^.]*variable_scale|variable_scale[^.]*already",
    "marginal extrema": r"jointly attainable",
    "inertia metric is not Gauss": r"Gauss's principle",
    "conventions not physiology": r"conventions?[^.]*not[^.]*physiolog",
    "declared measure": r"declared measure",
    "under review": r"under review",
    "corrector is not the nearest point": r"nearest-point",
    "quadratic tangent residual": r"O\(h\^2\)",
}


@pytest.mark.parametrize("name", sorted(BINDING_PATTERNS))
def test_binding_qualification_is_stated(name: str) -> None:
    flat = " ".join(_text().split())
    assert re.search(BINDING_PATTERNS[name], flat, re.IGNORECASE), name


def test_forbidden_claims_are_absent() -> None:
    lower = _text().lower()
    assert "cubic" not in lower, "no cubic-order corrector claim is allowed"
    assert "chebyshev radius bound" not in lower
    assert "exact second-order-cone envelope" not in lower
    assert "m - \\operatorname{rank} g" not in lower or "strictly" in lower


def test_attribution_contract_is_embedded_in_the_identifiability_section() -> None:
    text = _text()
    include = text.index(INCLUDE)
    assert text.index("{#sec-identifiable}") < include < text.index("{#sec-time}")


def test_no_executable_cells_and_listings_are_short_and_use_src_tools() -> None:
    text = _text()
    assert "```{python" not in text, "the page must render without a Jupyter kernel"
    blocks = re.findall(r"```python\n(.*?)```", text, re.DOTALL)
    assert blocks, "the article shows how to reproduce the numbers"
    for block in blocks:
        assert len(block.strip().splitlines()) <= 25
        assert "src.tools" in block


# ------------------------------------------------------------------------ 3. cross-links


def _heading_slug(title: str) -> str:
    """Pandoc's automatic identifier for a heading."""
    cleaned = re.sub(r"\{[^}]*\}", "", title)
    cleaned = re.sub(r"[^\w\s.-]", "", cleaned.lower()).strip()
    return re.sub(r"\s+", "-", cleaned)


def _anchors(path: Path) -> set[str]:
    anchors: set[str] = set()
    inside = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if FENCE.match(line):
            inside = not inside
            continue
        if inside:
            continue
        anchors.update(re.findall(r"\{[^}]*#([A-Za-z0-9_:-]+)", line))
        heading = re.match(r"^#{1,6}\s+(.*)$", line)
        if heading:
            anchors.add(_heading_slug(heading.group(1)))
    return anchors


def test_in_page_anchor_links_resolve() -> None:
    anchors = _anchors(ARTICLE)
    links = {frag for _, line in _body_lines() for frag in re.findall(r"\]\(#([^)\s]+)\)", line)}
    assert links, "expected in-page links to the propositions"
    assert not links - anchors, sorted(links - anchors)
    assert {f"prop-p{k}" for k in range(1, 8)} <= anchors


def test_quarto_section_references_resolve() -> None:
    anchors = _anchors(ARTICLE)
    refs = set(re.findall(r"(?<![\w`])@((?:sec|eq|tbl|fig)-[A-Za-z0-9_-]+)", _text()))
    assert refs, "expected @sec- cross-references"
    assert not refs - anchors, sorted(refs - anchors)


def test_links_to_other_pages_resolve_to_existing_anchors() -> None:
    checked = 0
    for _, line in _body_lines():
        for target in re.findall(r"\]\((?!https?://|#|mailto:)([^)\s]+)\)", line):
            page, _, fragment = target.partition("#")
            if not page.endswith(".html"):
                continue
            source = (ARTICLE.parent / page).with_suffix(".qmd").resolve()
            assert source.is_file(), f"{target}: {source} does not exist"
            if fragment:
                assert fragment in _anchors(source), f"{target}: anchor missing"
            checked += 1
    assert checked >= 5


def test_required_related_pages_are_linked() -> None:
    text = _text()
    assert "null-space-constraint-jacobian.html" in text
    assert (
        "degrees-of-freedom-and-dimensionality.html#infinite-solution-sets-and-finite-search"
        in text
    )
    assert "zero-torque-counterfactual.html" in text


def test_companion_names_in_the_article_exist_in_the_code() -> None:
    text = _text()
    linear_names = [
        "affine_fibre",
        "weighted_representative",
        "rescaled_representative",
        "reduced_quadratic",
        "kkt_minimiser",
        "functional_invariance",
        "functional_interval",
        "leakage_bound",
        "framewise_vs_coupled_envelope",
        "three_muscle_example",
        "grip_example",
    ]
    continuation_names = [
        "predictor_corrector_step",
        "tangent_step_residual",
        "trace_manifold",
        "RankChangeError",
    ]
    for module, names in ((linear_module, linear_names), (continuation_module, continuation_names)):
        for name in names:
            assert hasattr(module, name), name
            assert f"`{name}`" in text, f"{name} is not named in the article"


def test_upstreamdrift_section_marks_code_under_review_without_pinning() -> None:
    text = _text()
    section = text[text.index("{#sec-upstreamdrift}") :]
    section = section[: section.index("## Related Articles")]
    for number in PR_NUMBERS:
        assert f"/pull/{number}" in section, number
    assert "12593" in section
    assert "after_one_solution.md" in section
    assert not re.search(r"\b[0-9a-f]{40}\b", text), "no commit SHA may be pinned in this page"
    assert not re.search(r"UpstreamDrift/(blob|tree|commit)/", text)
    # Rows cross-reference the sections so the rendered numbers stay right even though the
    # shared attribution include adds a numbered heading of its own.
    rows = re.findall(r"^\|\s*@(sec-[a-z-]+)\b", section, re.MULTILINE)
    assert rows == SECTION_IDS, "one mapping row per section, in order"
    for api in (
        "classify_functional",
        "FunctionalStatus",
        "functional_record",
        "attribution_quantities",
        "static_envelopes",
        "x_functional_quantities",
        "hit_and_run",
        "FeasibleSet",
        "chebyshev_margin",
        "interior_point",
        "local_chart",
        "predictor_corrector_step",
        "ManifoldSingularityError",
        "ManifoldConvergenceError",
        "ActivationFiber",
        "hull_dimension",
        "sample_result",
        "level_subfibre_dimension",
        "dimension_accounting",
        "trajectory_envelope",
    ):
        assert api in section, api


# ------------------------------------------------------------------------ bibliography


def _bib_entries(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    parts = re.split(r"^@(\w+)\s*\{\s*([^,\s]+),", text, flags=re.MULTILINE)
    return {parts[i + 1]: parts[i + 2] for i in range(1, len(parts) - 2, 3)}


def _cited_keys() -> set[str]:
    text = re.sub(r"```.*?```", "", _text(), flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", "", text)
    candidates = set(re.findall(r"(?<![\w/])@([A-Za-z][A-Za-z0-9:_-]*)", text))
    ignored = ("sec-", "eq-", "tbl-", "fig-", "lst-", "prp-", "thm-")
    return {key for key in candidates if not key.startswith(ignored)}


def test_citations_resolve_and_new_bibliography_has_no_unused_or_duplicate_key() -> None:
    front, _ = split_frontmatter(_text())
    listed = front["bibliography"]
    listed = [listed] if isinstance(listed, str) else listed
    available: set[str] = set()
    for item in listed:
        available |= set(_bib_entries((ARTICLE.parent / item).resolve()))
    cited = _cited_keys()
    assert cited, "the article cites its sources"
    assert not cited - available, sorted(cited - available)
    new_keys = set(_bib_entries(NEW_BIB))
    assert new_keys <= cited, f"unused entries: {sorted(new_keys - cited)}"
    for other in sorted((ROOT / "references").glob("*.bib")):
        if other != NEW_BIB:
            assert not new_keys & set(_bib_entries(other)), f"duplicate key with {other.name}"


def test_new_bibliography_entries_are_complete_and_verifiable() -> None:
    entries = _bib_entries(NEW_BIB)
    assert len(entries) >= 6
    for key, body in entries.items():
        for field in ("author", "title", "year"):
            assert re.search(rf"\b{field}\s*=", body), f"{key} lacks {field}"
        assert re.search(r"\bdoi\s*=\s*\{10\.\d{4,9}/[^}\s]+\}", body), f"{key} lacks a DOI"
        assert "et al" not in body.lower(), key


# ------------------------------------------------------------------------------- 4. loader


def test_loader_returns_sections_and_validates_its_arguments(tmp_path: Path) -> None:
    document = load_examples()
    assert document["schema_version"] == 1
    assert {"linear", "continuation"} <= set(document["sections"])
    assert example_section("linear")["p1"]["survey"]
    with pytest.raises(KeyError, match="unknown"):
        example_section("not-a-section")
    with pytest.raises(TypeError):
        example_section(7)  # type: ignore[arg-type]
    with pytest.raises(FileNotFoundError):
        load_examples(tmp_path / "missing.json")
    stale = tmp_path / "stale.json"
    stale.write_text(json.dumps({"schema_version": 99, "sections": {}}), encoding="utf-8")
    with pytest.raises(ValueError, match="schema_version"):
        load_examples(stale)
    broken = tmp_path / "broken.json"
    broken.write_text(json.dumps({"schema_version": 1}), encoding="utf-8")
    with pytest.raises(ValueError, match="sections"):
        load_examples(broken)


def test_loader_returns_independent_copies() -> None:
    first: dict[str, Any] = example_section("linear")
    first["p1"]["survey"].clear()
    assert example_section("linear")["p1"]["survey"]
