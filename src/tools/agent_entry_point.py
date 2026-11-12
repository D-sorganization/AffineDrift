"""Machine-readable agent entry points (llms.txt / llms-full.txt) for AffineDrift (#5596).

The canonical page manifest lives in ``data/agent/canonical_pages.json``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "data/agent/canonical_pages.json"
LLMS_PATH = ROOT / "llms.txt"
LLMS_FULL_PATH = ROOT / "llms-full.txt"
SCHEMA = "affinedrift/agent-canonical-pages/v1"


@dataclass(frozen=True)
class AgentPage:
    """One curated page or artifact for agents."""

    title: str
    path: str
    source: str
    summary: str
    artifacts: tuple[str, ...]


@dataclass(frozen=True)
class AgentSection:
    """Grouped pages under an llms.txt H2 section."""

    name: str
    pages: tuple[AgentPage, ...]


@dataclass(frozen=True)
class AgentManifest:
    """Parsed canonical-pages manifest."""

    site_url: str
    repository_url: str
    reading_order_note: str
    sections: tuple[AgentSection, ...]


def _page(raw: dict[str, Any]) -> AgentPage:
    """Parse one manifest page entry."""
    artifacts = raw.get("artifacts") or []
    if not isinstance(artifacts, list):
        raise ValueError("artifacts must be a list when present")
    return AgentPage(
        title=str(raw["title"]),
        path=str(raw["path"]),
        source=str(raw["source"]),
        summary=str(raw["summary"]),
        artifacts=tuple(str(item) for item in artifacts),
    )


def load_manifest(text: str) -> AgentManifest:
    """Parse and validate ``data/agent/canonical_pages.json`` content."""
    payload = json.loads(text)
    if payload.get("schema") != SCHEMA:
        raise ValueError(f"unsupported manifest schema: {payload.get('schema')!r}")
    sections: list[AgentSection] = []
    for block in payload["sections"]:
        pages = tuple(_page(entry) for entry in block["pages"])
        sections.append(AgentSection(str(block["name"]), pages))
    if not sections:
        raise ValueError("manifest must contain at least one section")
    return AgentManifest(
        site_url=str(payload["site_url"]).rstrip("/"),
        repository_url=str(payload["repository_url"]).rstrip("/"),
        reading_order_note=str(payload.get("reading_order_note", "")),
        sections=tuple(sections),
    )


def _abs_url(site_url: str, path: str) -> str:
    """Return an absolute URL for a site-relative or external path."""
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return f"{site_url}{path}"


def _link_line(site_url: str, page: AgentPage) -> str:
    """Format one llms.txt bullet with title, URL, and summary."""
    url = _abs_url(site_url, page.path)
    return f"- [{page.title}]({url}): {page.summary}"


def render_llms_txt(manifest: AgentManifest) -> str:
    """Render the concise site-root ``llms.txt`` file."""
    lines = [
        "# AffineDrift",
        "",
        "> Control-affine golf swing research, educational textbooks, and a governed "
        "companion catalog for UpstreamDrift models.",
        "",
        manifest.reading_order_note,
        "",
        "## Notation and Conventions",
    ]
    for section in manifest.sections:
        lines.extend(["", f"## {section.name}"])
        for page in section.pages:
            lines.append(_link_line(manifest.site_url, page))
    lines.extend(
        [
            "",
            "## Machine-Readable Registries",
            f"- [Symbol registry]({manifest.site_url}/data/symbol_references.json): "
            "Equation symbols generated from NOTATION.md",
            f"- [Canonical pages manifest]({manifest.site_url}/data/agent/canonical_pages.json): "
            "Structured list of agent entry pages",
            "",
            "## Optional",
            f"- [Repository README]({manifest.repository_url}/blob/main/README.md): "
            "Build commands and local development",
            f"- [SPEC.md]({manifest.repository_url}/blob/main/SPEC.md): "
            "Repository specification and architecture pointers",
            "",
        ]
    )
    return "\n".join(lines)


def render_llms_full_txt(manifest: AgentManifest) -> str:
    """Render ``llms-full.txt`` with per-page source paths and artifacts."""
    lines = [
        "# AffineDrift — Full Agent Index",
        "",
        "> Expanded index with repository paths and bundled artifacts. "
        "Prefer ``llms.txt`` when context is limited.",
        "",
        f"Site: {manifest.site_url}",
        f"Repository: {manifest.repository_url}",
        "",
        manifest.reading_order_note,
        "",
    ]
    for section in manifest.sections:
        lines.extend([f"## {section.name}", ""])
        for page in section.pages:
            url = _abs_url(manifest.site_url, page.path)
            lines.append(f"### {page.title}")
            lines.append(f"- URL: {url}")
            lines.append(f"- Source: `{page.source}`")
            lines.append(f"- Summary: {page.summary}")
            if page.artifacts:
                joined = ", ".join(f"`{item}`" for item in page.artifacts)
                lines.append(f"- Artifacts: {joined}")
            lines.append("")
    lines.extend(
        [
            "## Structured Metadata",
            "- `data/symbol_references.json` — schema `affinedrift/symbol-references/v2`",
            "- `schemas/symbol-references-v2.schema.json` — JSON Schema for the registry",
            "- `data/trust/claim_registry.json` — governed claims with evidence paths",
            "- `data/research_protocols/library.json` — research protocol catalog",
            "",
        ]
    )
    return "\n".join(lines)


def render_both(manifest: AgentManifest) -> tuple[str, str]:
    """Return ``(llms.txt, llms-full.txt)`` bodies, each with a trailing newline."""
    return render_llms_txt(manifest) + "\n", render_llms_full_txt(manifest) + "\n"
