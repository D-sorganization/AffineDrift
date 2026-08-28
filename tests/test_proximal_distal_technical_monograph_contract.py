"""Publication contracts for the canonical proximal-distal technical monograph in AffineDrift."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
MONOGRAPH_DIR = ROOT / "articles/proximal_distal_energy_transfer"
INDEX_QMD = MONOGRAPH_DIR / "index.qmd"
CHAPTERS_DIR = MONOGRAPH_DIR / "chapters"
FIGURES_DIR = MONOGRAPH_DIR / "figures"
PDF_FILE = MONOGRAPH_DIR / "proximal_distal_energy_transfer.pdf"
BIB_FILE = MONOGRAPH_DIR / "references.bib"
SOURCE_MANIFEST = MONOGRAPH_DIR / "source_manifest.json"
MONOGRAPH_CSS = MONOGRAPH_DIR / "monograph.css"

EXPECTED_CHAPTER_COUNT = 36
EXPECTED_MIN_PAGE_COUNT = 181
EXPECTED_MIN_WORD_COUNT = 69_000
EXPECTED_SOURCE_COMMIT = "1b867e9da38dc6c3a321e0f7c199586fff5cf7be"
EXPECTED_RELEASE_MANIFEST_SHA256 = (
    "91a5c35bad5ea2bd5fc2737b8e0408d1256fac2f026927399e6e6b83018d9b9f"
)
EXPECTED_CLAIM_REGISTRY_SHA256 = "dc07b321b913fc2d4af2f74a838b76b5f63cda527fa274f9d34f8efecb5e11a6"
EXPECTED_PDF_SHA256 = "92bfaca850ac459cc431e573be8c0288af51ceab4d28759d02c67c602274ee8b"


def test_technical_monograph_files_exist_and_are_complete() -> None:
    """Verify that the master QMD, PDF, bibliography, and all chapters exist."""
    assert INDEX_QMD.is_file(), f"{INDEX_QMD} is missing"
    assert PDF_FILE.is_file(), f"{PDF_FILE} is missing"
    assert PDF_FILE.stat().st_size > 1_000_000, "PDF file is unexpectedly small"
    assert BIB_FILE.is_file(), f"{BIB_FILE} is missing"

    chapter_files = list(CHAPTERS_DIR.glob("*.qmd"))
    assert (
        len(chapter_files) == EXPECTED_CHAPTER_COUNT
    ), f"Expected {EXPECTED_CHAPTER_COUNT} chapters, found {len(chapter_files)}"


def test_technical_monograph_index_includes_all_chapters() -> None:
    """Verify that index.qmd contains Quarto includes for every chapter."""
    index_text = INDEX_QMD.read_text(encoding="utf-8")
    for chapter in CHAPTERS_DIR.glob("*.qmd"):
        include_tag = f"include chapters/{chapter.name}"
        assert include_tag in index_text, f"Missing include for {chapter.name} in index.qmd"


def test_technical_monograph_pdf_metrics() -> None:
    """Assert that the compiled PDF meets the minimum page count and word density."""
    reader = PdfReader(PDF_FILE)
    page_count = len(reader.pages)
    assert (
        page_count >= EXPECTED_MIN_PAGE_COUNT
    ), f"Expected at least {EXPECTED_MIN_PAGE_COUNT} pages, got {page_count}"

    extracted_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    extracted_words = extracted_text.split()
    assert (
        len(extracted_words) >= EXPECTED_MIN_WORD_COUNT
    ), f"Expected at least {EXPECTED_MIN_WORD_COUNT} words, got {len(extracted_words)}"


def test_technical_monograph_declares_immutable_scientific_source() -> None:
    """Verify the publication identifies and matches its scientific source."""
    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    reader = PdfReader(PDF_FILE)
    pdf_bytes = PDF_FILE.read_bytes()

    assert manifest["schema_version"] == "proximal-distal-publication-source-v2"
    assert manifest["source"]["repository"] == "D-sorganization/UpstreamDrift"
    assert manifest["source"]["commit"] == EXPECTED_SOURCE_COMMIT
    assert manifest["source"]["release_manifest_sha256"] == EXPECTED_RELEASE_MANIFEST_SHA256
    assert manifest["source"]["claim_registry"] == {
        "path": "docs/research/proximal_distal_energy_transfer/data/claim_audit_registry.json",
        "sha256": EXPECTED_CLAIM_REGISTRY_SHA256,
        "bytes": 1_630_883,
    }
    assert manifest["source"]["pdf_sha256"] == EXPECTED_PDF_SHA256
    assert manifest["publication"]["repository"] == "D-sorganization/AffineDrift"
    assert manifest["publication"]["page_count"] == len(reader.pages)
    assert manifest["publication"]["bytes"] == len(pdf_bytes)
    assert manifest["publication"]["pdf_sha256"] == EXPECTED_PDF_SHA256
    assert manifest["publication"]["pdf_sha256"] == hashlib.sha256(pdf_bytes).hexdigest()
    assert manifest["source"]["pdf_sha256"] == manifest["publication"]["pdf_sha256"]
    assert manifest["generation_environment"] == {
        "creator": reader.metadata.creator,
        "producer": reader.metadata.producer,
        "tex_banner": reader.metadata["/PTEX.FullBanner"],
        "pdf_creation_date": reader.metadata.creation_date_raw,
    }
    assert manifest["qualification"] == {
        "profile": "computational",
        "computational_release": True,
        "archival_publication": False,
        "archival_gaps": [
            "pdf-not-tagged",
            "type3-font-resource",
            "unembedded-font-resource",
        ],
    }
    assert f"({len(reader.pages)} pages," in INDEX_QMD.read_text(encoding="utf-8")


def test_upstream_evidence_links_use_the_published_source_commit() -> None:
    """Keep source-only evidence links on the same immutable release authority."""
    upstream_blob = re.compile(
        r"https://github\.com/D-sorganization/UpstreamDrift/(?:blob|tree)/([^/]+)/"
    )
    linked_commits = {
        commit
        for chapter in CHAPTERS_DIR.glob("*.qmd")
        for commit in upstream_blob.findall(chapter.read_text(encoding="utf-8"))
    }

    assert linked_commits == {EXPECTED_SOURCE_COMMIT}


def test_technical_monograph_uses_a_concise_scientific_abstract() -> None:
    """Keep publication metadata readable without turning the abstract into a chapter."""
    index_text = INDEX_QMD.read_text(encoding="utf-8")
    abstract_match = re.search(
        r"^abstract: \|\n(?P<body>.*?)^keywords:\n", index_text, re.MULTILINE | re.DOTALL
    )

    assert abstract_match is not None, "index.qmd must declare an abstract before keywords"
    abstract_words = abstract_match.group("body").split()
    assert 150 <= len(abstract_words) <= 350
    assert "css: monograph.css" in index_text
    assert "#title-block-header.quarto-title-block" in MONOGRAPH_CSS.read_text(encoding="utf-8")


def test_technical_monograph_figures_exist() -> None:
    """Assert that figures referenced in the chapters exist in figures directory."""
    for chapter in CHAPTERS_DIR.glob("*.qmd"):
        chapter_text = chapter.read_text(encoding="utf-8")
        for match in re.finditer(r"\[.*?\]\(([^)]+?\.(?:pdf|svg|png))\)", chapter_text):
            target_path = match.group(1)
            if target_path.startswith("http://") or target_path.startswith("https://"):
                continue
            assert target_path.startswith(
                "figures/"
            ), f"Figure path '{target_path}' in {chapter.name} must start with 'figures/' convention"
            fig_rel = target_path.removeprefix("figures/")
            target_file = FIGURES_DIR / fig_rel
            assert (
                target_file.is_file()
            ), f"Figure '{target_path}' referenced in {chapter.name} not found in {FIGURES_DIR}"


def test_technical_monograph_quarto_registration() -> None:
    """Assert that the technical monograph is registered in _quarto.yml resources, sidebar, and navbar."""
    quarto_yml = (ROOT / "_quarto.yml").read_text(encoding="utf-8")
    assert (
        "articles/proximal_distal_energy_transfer/proximal_distal_energy_transfer.pdf" in quarto_yml
    )
    assert "articles/proximal_distal_energy_transfer/source_manifest.json" in quarto_yml
    assert "articles/proximal_distal_energy_transfer/index.html" in quarto_yml
    assert "Proximal-to-Distal Energy Transfer" in quarto_yml


def test_technical_monograph_article_index_registration() -> None:
    """Assert that the technical monograph is cataloged in resources/articles.qmd."""
    articles_catalog = (ROOT / "resources/articles.qmd").read_text(encoding="utf-8")
    assert "articles/proximal_distal_energy_transfer/index.html" in articles_catalog
