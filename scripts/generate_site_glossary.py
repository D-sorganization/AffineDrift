#!/usr/bin/env python3
"""scripts/generate_site_glossary.py

Compiles data/glossary.yml into pages/glossary.qmd.
Adheres strictly to Issue #4490 [WEB-01.5].
"""

import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_ROOT / "data" / "glossary.yml"
OUTPUT_QMD = REPO_ROOT / "pages" / "glossary.qmd"


def load_glossary() -> dict[str, dict[str, Any]]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing {DATA_PATH}")
    with open(DATA_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("Glossary YAML must be a dictionary of term entries")
    return data


def validate_canonical_pages(glossary: dict[str, dict[str, Any]]) -> list[str]:
    errors = []
    for key, entry in glossary.items():
        page = entry.get("canonical_page", "")
        if not page:
            errors.append(f"Term '{key}' missing canonical_page")
            continue
        p = page.replace(".html", ".qmd")
        if p.startswith("/"):
            p = p[1:]
        resolved = REPO_ROOT / p
        alt_resolved = REPO_ROOT / page
        if not resolved.exists() and not alt_resolved.exists():
            errors.append(f"Term '{key}' canonical_page '{page}' does not exist on disk")
    return errors


def generate_glossary_qmd(glossary: dict[str, dict[str, Any]]) -> str:
    # Group terms alphabetically by first letter of name
    grouped = defaultdict(list)
    sorted_keys = sorted(glossary.keys(), key=lambda k: glossary[k]["name"].lower())
    for k in sorted_keys:
        letter = glossary[k]["name"][0].upper()
        grouped[letter].append((k, glossary[k]))

    alphabet = sorted(grouped.keys())

    lines: list[str] = [
        "---",
        'title: "Site Glossary"',
        'description: "Site-wide glossary of biomechanics, control theory, golf physics, and governance terms with plain-language and technical definitions."',
        "toc: true",
        "toc-depth: 2",
        "categories:",
        "  - site-information",
        "  - reference",
        "---",
        "",
        ":::{.lead}",
        "A rigorous, accessible glossary bridging intuitive plain-language concepts, mathematical definitions, and canonical research articles across the AffineDrift publication.",
        ":::",
        "",
        '```{=html}\n<nav class="glossary-nav" aria-label="Alphabetical term index">',
        '  <div class="glossary-nav__letters">',
    ]

    for letter in alphabet:
        lines.append(f'    <a href="#{letter.lower()}" class="glossary-nav__letter">{letter}</a>')

    lines.extend(
        [
            "  </div>",
            "</nav>\n```",
            "",
        ]
    )

    for letter in alphabet:
        lines.append(f"## {letter} {{#{letter.lower()}}}\n")
        for key, term in grouped[letter]:
            name = term["name"]
            plain = term["plain"]
            technical = term["technical"]
            canonical = term["canonical_page"]
            symbols = term.get("symbols", [])

            lines.append(f"### {name} {{#{key}}}\n")
            lines.append(f'::: {{.glossary-entry id="def-{key}"}}\n')
            lines.append(f"**Plain Language:** {plain}\n")
            lines.append(f"**Technical Definition:** {technical}\n")

            if symbols:
                sym_list = ", ".join(f"${s}$" if not s.startswith("$") else s for s in symbols)
                lines.append(f"**Symbols / Notation:** {sym_list}\n")

            target = canonical.lstrip("/")
            if target.startswith("pages/"):
                link_target = target[len("pages/") :]
            else:
                link_target = f"../{target}"

            if link_target.endswith(".qmd"):
                link_target = link_target[:-4] + ".html"

            lines.append(f"[Read in Context &rarr;]({link_target}){{.glossary-canonical-link}}\n")
            lines.append(":::\n")

    lines.extend(
        [
            "## Related Articles\n",
            "- [Overview](overview.html) — Scope, evidence standards, and reading paths",
            "- [Drifter Manifesto](drifter-manifesto.html) — Canonical series on control-affine modeling of the golf swing",
            "- [Mathematical Notation Reference](notation.html) — Normative symbol conventions and control-affine definitions",
            "- [Article Index](../resources/articles.html) — Complete inventory of published articles\n",
        ]
    )

    return "\n".join(lines)


def main() -> int:
    try:
        glossary = load_glossary()
    except Exception as exc:
        print(f"Error loading glossary: {exc}", file=sys.stderr)
        return 1

    errors = validate_canonical_pages(glossary)
    if errors:
        print("Canonical page validation errors:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    content = generate_glossary_qmd(glossary)
    OUTPUT_QMD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_QMD.write_text(content, encoding="utf-8")
    print(
        f"Successfully generated {OUTPUT_QMD} with {len(glossary)} terms across {len(set(glossary.keys()))} keys."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
