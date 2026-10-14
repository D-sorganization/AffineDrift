"""Unit and contract tests verifying recovered Forward Dynamics Matching research book structure."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
BOOK_DIR = REPO_ROOT / "articles" / "forward_dynamics_matching"
DOCS_DIR = REPO_ROOT / "docs" / "development" / "forward-dynamics-matching"
REFERENCES_DIR = REPO_ROOT / "references"
QUARTO_CONFIG = REPO_ROOT / "_quarto.yml"

EXPECTED_CHAPTER_STEMS = (
    "01_problem",
    "02_upstream_inventory",
    "03_historical_lessons",
    "04_measurements",
    "05_inverse_methods",
    "06_shooting",
    "07_collocation",
    "08_control_bases",
    "09_contact",
    "10_gradients",
    "11_muscles",
    "12_state_estimation",
    "13_validation",
    "14_bayesian",
    "15_identifiability",
    "16_dimensions",
    "17_sparse_discovery",
    "18_adaptive_design",
    "19_research_synthesis",
    "20_latent_dynamics",
    "21_experimental_design",
    "22_learning_tracking",
    "23_software_contracts",
    "24_references",
    "25_maintenance",
    "26_neural_proposals",
)


def _compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def test_book_directory_structure_and_artifacts() -> None:
    """The book directory must contain the Quarto configuration, landing page, manifest, and PDF preview."""
    assert BOOK_DIR.is_dir(), f"Book directory missing: {BOOK_DIR}"

    metadata_file = BOOK_DIR / "_metadata.yml"
    assert metadata_file.is_file(), "Missing _metadata.yml"
    metadata = yaml.safe_load(metadata_file.read_text(encoding="utf-8"))
    assert isinstance(metadata, dict)

    local_quarto = BOOK_DIR / "_quarto.yml"
    assert local_quarto.is_file(), "Missing articles/forward_dynamics_matching/_quarto.yml"
    local_cfg = yaml.safe_load(local_quarto.read_text(encoding="utf-8"))
    assert isinstance(local_cfg, dict)

    index_page = BOOK_DIR / "index.qmd"
    assert index_page.is_file(), "Missing index.qmd"
    index_text = index_page.read_text(encoding="utf-8")
    assert "Forward Dynamics Matching" in index_text
    assert "matching-forward-dynamics-draft.pdf" in index_text

    pdf_draft = BOOK_DIR / "matching-forward-dynamics-draft.pdf"
    assert pdf_draft.is_file(), "Missing matching-forward-dynamics-draft.pdf"
    assert pdf_draft.stat().st_size > 500_000, "Draft PDF preview appears truncated or empty"

    manifest_file = BOOK_DIR / "source_manifest.json"
    assert manifest_file.is_file(), "Missing source_manifest.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert manifest.get("status") == "local_manuscript_publication_pending"
    assert manifest.get("upstream_commit") == "d7c7d07add0d7407a5a3376d5fe4a97aee9112a0"

    link_val_file = BOOK_DIR / "link_validation.json"
    assert link_val_file.is_file(), "Missing link_validation.json"


def test_development_recovery_documentation() -> None:
    """The development docs must preserve the cloud recovery receipt, validation log, and source audit."""
    assert DOCS_DIR.is_dir(), f"Recovery docs directory missing: {DOCS_DIR}"

    receipt_file = DOCS_DIR / "recovery-receipt.json"
    assert receipt_file.is_file(), "Missing recovery-receipt.json"
    receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
    assert receipt.get("issue") == 4948
    assert receipt.get("cloud_session") == "01a10a7a-86c9-7143-b80c-fb9d7512d033"
    assert (
        receipt.get("bundle_sha256")
        == "e35ac524244db6e4796cca1ef5334e5ac06eab0f2d89f5ae5831ce33c637a9be"
    )
    assert receipt.get("bundle_bytes") == 710165

    for doc_name in (
        "recovery.md",
        "validation.md",
        "upstream-source-audit.md",
        "offline-checks.json",
        "preview-build-command.json",
    ):
        p = DOCS_DIR / doc_name
        assert p.is_file(), f"Missing recovery doc: {doc_name}"
        assert p.stat().st_size > 0, f"Empty recovery doc: {doc_name}"


def test_all_26_chapters_exist_with_valid_headings_and_manifest_hashes() -> None:
    """All 26 chapters must exist, contain H1 titles, and match source_manifest.json hashes."""
    manifest_file = BOOK_DIR / "source_manifest.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    manifest_map = {entry["path"]: entry["sha256"] for entry in manifest["files"]}

    for stem in EXPECTED_CHAPTER_STEMS:
        chapter_file = BOOK_DIR / f"{stem}.qmd"
        assert chapter_file.is_file(), f"Missing chapter: {chapter_file.name}"
        content = chapter_file.read_text(encoding="utf-8")
        assert len(content.strip()) > 200, f"Chapter {stem} is too short or empty"

        from src.tools.utils.frontmatter import split_frontmatter

        _, body = split_frontmatter(content)
        body_lines = [line.strip() for line in body.splitlines() if line.strip()]
        assert body_lines, f"Chapter {stem} has no non-empty body lines"
        assert body_lines[0].startswith(
            "# "
        ), f"Chapter {stem} first heading is not H1: {body_lines[0]}"

        rel_posix = chapter_file.relative_to(REPO_ROOT).as_posix()
        assert rel_posix in manifest_map, f"{rel_posix} missing from source_manifest.json"
        body_sha = hashlib.sha256(body.lstrip().encode("utf-8")).hexdigest()
        assert (
            body_sha == manifest_map[rel_posix]
        ), f"Digest mismatch for {rel_posix}: expected {manifest_map[rel_posix]}, got {body_sha}"


def test_quarto_navigation_sidebar_and_resources_integration() -> None:
    """The root _quarto.yml must configure the forward-matching-nav sidebar, resources, and bibliography."""
    quarto_text = QUARTO_CONFIG.read_text(encoding="utf-8")
    cfg = yaml.safe_load(quarto_text)

    # Check project resources
    resources = cfg.get("project", {}).get("resources", [])
    assert (
        "articles/forward_dynamics_matching/matching-forward-dynamics-draft.pdf" in resources
    ), "Draft PDF missing from project.resources in _quarto.yml"
    assert (
        "articles/forward_dynamics_matching/source_manifest.json" in resources
    ), "source_manifest.json missing from project.resources in _quarto.yml"

    # Check sidebar
    sidebars = cfg.get("website", {}).get("sidebar", [])
    forward_nav = next((s for s in sidebars if s.get("id") == "forward-matching-nav"), None)
    assert forward_nav is not None, "forward-matching-nav sidebar not found in _quarto.yml"

    sidebar_hrefs = [item.get("href") for item in forward_nav.get("contents", [])]
    assert "articles/forward_dynamics_matching/index.html" in sidebar_hrefs
    for stem in EXPECTED_CHAPTER_STEMS:
        expected_href = f"articles/forward_dynamics_matching/{stem}.html"
        assert expected_href in sidebar_hrefs, f"Sidebar missing chapter link: {expected_href}"

    # Check bibliography
    bib_list = cfg.get("bibliography", [])
    assert (
        "references/forward-dynamics-matching.bib" in bib_list
    ), "references/forward-dynamics-matching.bib missing from bibliography in _quarto.yml"


def test_bibliography_citations_and_cross_references() -> None:
    """Every citation in the recovered chapters must resolve against bibliography files."""
    bib_file = REFERENCES_DIR / "forward-dynamics-matching.bib"
    assert bib_file.is_file(), "Missing references/forward-dynamics-matching.bib"
    assert bib_file.stat().st_size > 0, "references/forward-dynamics-matching.bib is empty"

    known_keys: set[str] = set()
    for bib_path in REFERENCES_DIR.glob("*.bib"):
        content = bib_path.read_text(encoding="utf-8", errors="ignore")
        for match in re.finditer(r"@\w+\s*\{\s*([^,\s]+)", content):
            known_keys.add(match.group(1).strip())

    citation_pattern = re.compile(r"@([A-Za-z0-9_:\-]+)")
    ignored_prefixes = ("fig-", "sec-", "eq-", "tbl-", "lst-")

    for qmd in BOOK_DIR.glob("*.qmd"):
        text = qmd.read_text(encoding="utf-8")
        for match in citation_pattern.finditer(text):
            key = match.group(1)
            if any(key.startswith(p) for p in ignored_prefixes):
                continue
            assert key in known_keys, f"Unresolved citation key '@{key}' in {qmd.name}"
