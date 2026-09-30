"""Generate the datasets catalog cards from data/datasets.yml (WEB-07.7, #4549).

Reads the site's dataset catalog source of truth and renders it into the
generated block of resources/resources-datasets.qmd, so licence, access, and
checksum fields cannot drift out of sync with the catalog data.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from src.tools.utils import escape_html

GENERATED_BEGIN = "<!-- GENERATED:BEGIN datasets-catalog -->"
GENERATED_END = "<!-- GENERATED:END datasets-catalog -->"
_GENERATED_BLOCK = re.compile(
    re.escape(GENERATED_BEGIN) + r".*?" + re.escape(GENERATED_END), re.DOTALL
)

THIRD_PARTY_REQUIRED_FIELDS = (
    "id",
    "name",
    "description",
    "paper_url",
    "licence",
    "size",
    "modality",
    "access",
    "citation",
)
AFFINEDRIFT_REQUIRED_FIELDS = (
    "id",
    "name",
    "description",
    "directory",
    "licence",
    "modality",
    "access",
    "citation",
)


class DatasetCatalogError(ValueError):
    """Raised when data/datasets.yml or its referenced artefacts are invalid."""


@dataclass(frozen=True)
class ThirdPartyDataset:
    """One third-party dataset entry from data/datasets.yml."""

    id: str
    name: str
    description: str
    paper_url: str
    licence: str
    size: str
    modality: str
    access: str
    citation: str
    repo_url: str | None = None


@dataclass(frozen=True)
class FileChecksum:
    """A single file's name and SHA-256 digest."""

    filename: str
    sha256: str


@dataclass(frozen=True)
class AffineDriftArtifact:
    """One AffineDrift-owned data artefact directory from data/datasets.yml."""

    id: str
    name: str
    description: str
    directory: str
    licence: str
    modality: str
    access: str
    citation: str
    schema: str | None = None


@dataclass(frozen=True)
class DatasetCatalog:
    """The full parsed contents of data/datasets.yml."""

    third_party: tuple[ThirdPartyDataset, ...]
    affinedrift: tuple[AffineDriftArtifact, ...]


def _require_fields(entry: dict[str, Any], required: tuple[str, ...], section: str) -> None:
    """Fail loudly when a catalog entry is missing a required field (DbC boundary check)."""
    missing = [field for field in required if not entry.get(field)]
    if missing:
        entry_id = entry.get("id", "<unknown>")
        raise DatasetCatalogError(
            f"{section} entry {entry_id!r} is missing required field(s): {', '.join(missing)}"
        )


def _load_third_party(raw_entries: list[dict[str, Any]]) -> tuple[ThirdPartyDataset, ...]:
    """Validate and construct third-party dataset entries."""
    datasets = []
    for entry in raw_entries:
        _require_fields(entry, THIRD_PARTY_REQUIRED_FIELDS, "third_party")
        datasets.append(
            ThirdPartyDataset(
                id=entry["id"],
                name=entry["name"],
                description=entry["description"],
                paper_url=entry["paper_url"],
                licence=entry["licence"],
                size=entry["size"],
                modality=entry["modality"],
                access=entry["access"],
                citation=entry["citation"],
                repo_url=entry.get("repo_url"),
            )
        )
    return tuple(datasets)


def _load_affinedrift(raw_entries: list[dict[str, Any]]) -> tuple[AffineDriftArtifact, ...]:
    """Validate and construct AffineDrift-owned artefact entries."""
    artifacts = []
    for entry in raw_entries:
        _require_fields(entry, AFFINEDRIFT_REQUIRED_FIELDS, "affinedrift")
        artifacts.append(
            AffineDriftArtifact(
                id=entry["id"],
                name=entry["name"],
                description=entry["description"],
                directory=entry["directory"],
                licence=entry["licence"],
                modality=entry["modality"],
                access=entry["access"],
                citation=entry["citation"],
                schema=entry.get("schema"),
            )
        )
    return tuple(artifacts)


def load_catalog(path: Path) -> DatasetCatalog:
    """Load and validate data/datasets.yml.

    Raises:
        DatasetCatalogError: if any entry is missing a required field.
    """
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return DatasetCatalog(
        third_party=_load_third_party(raw.get("third_party", [])),
        affinedrift=_load_affinedrift(raw.get("affinedrift", [])),
    )


def compute_directory_checksums(repo_root: Path, directory: str) -> tuple[FileChecksum, ...]:
    """Hash every JSON file directly under `directory` (non-recursive, sorted by name)."""
    target = repo_root / directory
    if not target.is_dir():
        raise DatasetCatalogError(f"dataset artefact directory not found: {directory}")
    files = sorted(target.glob("*.json"))
    if not files:
        raise DatasetCatalogError(
            f"no JSON files found under dataset artefact directory: {directory}"
        )
    return tuple(
        FileChecksum(filename=f.name, sha256=hashlib.sha256(f.read_bytes()).hexdigest())
        for f in files
    )


def _link(href: str, text: str) -> str:
    """Render an escaped external link that also announces itself to screen readers."""
    return (
        f'<a href="{escape_html(href)}" target="_blank" rel="noopener">{escape_html(text)}'
        '<span class="sr-only"> (opens in a new tab)</span></a>'
    )


def _meta_rows(pairs: list[tuple[str, str]]) -> str:
    """Render (label, escaped-value) pairs as a definition-list of dt/dd rows."""
    rows = "\n".join(
        f'            <div class="resource-meta__row"><dt>{escape_html(label)}</dt>'
        f"<dd>{value}</dd></div>"
        for label, value in pairs
    )
    return f'          <dl class="resource-meta">\n{rows}\n          </dl>'


def render_third_party_card(entry: ThirdPartyDataset) -> str:
    """Render one third-party dataset as a resource-card."""
    meta = [
        ("Licence", escape_html(entry.licence)),
        ("Size", escape_html(entry.size)),
        ("Modality", escape_html(entry.modality)),
        ("Access", escape_html(entry.access)),
        ("Citation", escape_html(entry.citation)),
    ]
    if entry.repo_url:
        meta.append(("Repository", _link(entry.repo_url, entry.repo_url)))
    return (
        '        <div class="resource-card">\n'
        f"          <h2>{escape_html(entry.name)}</h2>\n"
        f'          <p class="resource-description">{escape_html(entry.description)}</p>\n'
        f"{_meta_rows(meta)}\n"
        f'          <a href="{escape_html(entry.paper_url)}" class="resource-link" '
        'target="_blank" rel="noopener">\n'
        "            Read Paper →\n"
        '          <span class="sr-only">(opens in a new tab)</span></a>\n'
        "        </div>"
    )


def _checksum_table(checksums: tuple[FileChecksum, ...]) -> str:
    """Render a per-file SHA-256 table for one AffineDrift data artefact directory."""
    rows = "\n".join(
        f"              <tr><td><code>{escape_html(c.filename)}</code></td>"
        f"<td><code>{c.sha256}</code></td></tr>"
        for c in checksums
    )
    return (
        '          <table class="resource-checksums">\n'
        "            <caption>SHA-256 checksums</caption>\n"
        "            <thead><tr><th>File</th><th>SHA-256</th></tr></thead>\n"
        f"            <tbody>\n{rows}\n            </tbody>\n"
        "          </table>"
    )


def render_affinedrift_card(entry: AffineDriftArtifact, repo_root: Path) -> str:
    """Render one AffineDrift-owned data artefact directory as a resource-card."""
    checksums = compute_directory_checksums(repo_root, entry.directory)
    meta = [
        ("Licence", escape_html(entry.licence)),
        ("Modality", escape_html(entry.modality)),
        ("Access", escape_html(entry.access)),
        ("Directory", escape_html(entry.directory)),
        ("Citation", escape_html(entry.citation)),
    ]
    if entry.schema:
        meta.append(("Schema", escape_html(entry.schema)))
    return (
        '        <div class="resource-card">\n'
        f"          <h2>{escape_html(entry.name)}</h2>\n"
        f'          <p class="resource-description">{escape_html(entry.description)}</p>\n'
        f"{_meta_rows(meta)}\n"
        f"{_checksum_table(checksums)}\n"
        "        </div>"
    )


def render_third_party_section(datasets: tuple[ThirdPartyDataset, ...]) -> str:
    """Render the third-party datasets heading, intro, and card grid."""
    cards = "\n\n".join(render_third_party_card(d) for d in datasets)
    return (
        '        <div id="datasets-section" class="page-section">\n'
        '          <h1 class="section-heading">Datasets</h1>\n'
        "        </div>\n"
        '        <div class="resources-intro">\n'
        "          <p>\n"
        "            Third-party datasets used in golf swing biomechanics and sports-pose "
        "research. Licence, size, modality, and access terms are recorded here so they can be "
        "checked before reuse; see each entry's source for authoritative terms.\n"
        "          </p>\n"
        "        </div>\n"
        '        <div class="resource-grid">\n'
        f"{cards}\n"
        "        </div>"
    )


def render_affinedrift_section(artifacts: tuple[AffineDriftArtifact, ...], repo_root: Path) -> str:
    """Render the AffineDrift-owned data artefacts heading, intro, and card grid."""
    cards = "\n\n".join(render_affinedrift_card(a, repo_root) for a in artifacts)
    return (
        '        <div class="page-section">\n'
        '          <h2 class="section-heading">AffineDrift Data Artefacts</h2>\n'
        "          <p>\n"
        "            Data and schemas published directly from this repository, with a SHA-256 "
        "checksum for every file so a download can be verified against the version described "
        "here.\n"
        "          </p>\n"
        "        </div>\n"
        '        <div class="resource-grid">\n'
        f"{cards}\n"
        "        </div>"
    )


def render_catalog_block(catalog: DatasetCatalog, repo_root: Path) -> str:
    """Render the full generated block, markers included, for resources-datasets.qmd."""
    body = "\n\n".join(
        [
            render_third_party_section(catalog.third_party),
            render_affinedrift_section(catalog.affinedrift, repo_root),
        ]
    )
    return f"{GENERATED_BEGIN}\n{body}\n{GENERATED_END}"


def render_updated_qmd(qmd_path: Path, catalog: DatasetCatalog, repo_root: Path) -> str:
    """Return resources-datasets.qmd content with the generated block refreshed.

    Raises:
        DatasetCatalogError: if the file has no generated block to replace.
    """
    original = qmd_path.read_text(encoding="utf-8")
    if not _GENERATED_BLOCK.search(original):
        raise DatasetCatalogError(
            f"{qmd_path} has no {GENERATED_BEGIN} .. {GENERATED_END} block to replace"
        )
    replacement = render_catalog_block(catalog, repo_root)
    return _GENERATED_BLOCK.sub(lambda _match: replacement, original)
