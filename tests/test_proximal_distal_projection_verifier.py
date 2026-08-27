"""Contracts for the immutable UpstreamDrift publication projection."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.verify_proximal_distal_projection import (
    ProjectionError,
    projection_tree,
    verify_projection,
    verify_projection_lock,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLICATION_ROOT = REPO_ROOT / "articles" / "proximal_distal_energy_transfer"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _fixture(tmp_path: Path) -> tuple[Path, dict[str, object], dict[str, object], bytes]:
    root = tmp_path / "publication"
    (root / "figures").mkdir(parents=True)
    direct = b"source-identical\n"
    flattened = b"flattened figure"
    adapted = b"publisher adaptation\n"
    pdf = b"publication pdf"
    source_link = b"https://github.com/D-sorganization/UpstreamDrift/blob/main/file\n"
    pinned_link = source_link.replace(b"/main/", b"/abc123/")
    (root / "chapter.qmd").write_bytes(direct)
    (root / "linked.qmd").write_bytes(pinned_link)
    (root / "figures" / "plot.pdf").write_bytes(flattened)
    (root / "index.qmd").write_bytes(adapted)
    (root / "publication.pdf").write_bytes(pdf)
    publisher: dict[str, object] = {
        "source": {
            "repository": "D-sorganization/UpstreamDrift",
            "commit": "abc123",
            "root": "upstream/root",
            "pdf_sha256": _sha(pdf),
            "claim_registry": {
                "path": "upstream/root/data/claims.json",
                "sha256": _sha(b"claims"),
                "bytes": 6,
            },
        },
        "publication": {"pdf": "publication.pdf", "pdf_sha256": _sha(pdf)},
        "projection": {
            "adapted_files": {
                "index.qmd": {"sha256": _sha(adapted), "reason": "publisher metadata"}
            }
        },
    }
    upstream: dict[str, object] = {
        "artifacts": {
            "upstream/root/chapter.qmd": {"sha256": _sha(direct), "bytes": len(direct)},
            "upstream/root/linked.qmd": {
                "sha256": _sha(source_link),
                "bytes": len(source_link),
            },
            "upstream/root/data/study/figures/plot.pdf": {
                "sha256": _sha(flattened),
                "bytes": len(flattened),
            },
            "upstream/root/data/claims.json": {"sha256": _sha(b"claims"), "bytes": 6},
            "upstream/root/publication.pdf": {"sha256": _sha(pdf), "bytes": len(pdf)},
        }
    }
    file_count, tree_hash = projection_tree(root, "publication.pdf")
    projection = publisher["projection"]
    assert isinstance(projection, dict)
    projection.update({"file_count": file_count, "tree_sha256": tree_hash})
    return root, publisher, upstream, pdf


def test_projection_accepts_direct_flattened_and_declared_adapted_files(tmp_path: Path) -> None:
    root, publisher, upstream, pdf = _fixture(tmp_path)

    result = verify_projection(root, publisher, upstream, pdf)

    assert (result.source_identical, result.flattened, result.rewritten, result.adapted) == (
        1,
        1,
        1,
        1,
    )


@pytest.mark.parametrize("relative", ["chapter.qmd", "index.qmd"])
def test_projection_fails_closed_on_stale_source_or_adaptation(
    tmp_path: Path, relative: str
) -> None:
    root, publisher, upstream, pdf = _fixture(tmp_path)
    (root / relative).write_text("stale", encoding="utf-8")

    with pytest.raises(ProjectionError, match=relative):
        verify_projection(root, publisher, upstream, pdf)


def test_projection_rejects_ambiguous_flattened_source(tmp_path: Path) -> None:
    root, publisher, upstream, pdf = _fixture(tmp_path)
    artifacts = upstream["artifacts"]
    assert isinstance(artifacts, dict)
    artifacts["upstream/root/other/plot.pdf"] = artifacts[
        "upstream/root/data/study/figures/plot.pdf"
    ]

    with pytest.raises(ProjectionError, match="ambiguous"):
        verify_projection(root, publisher, upstream, pdf)


def test_projection_rejects_an_upstream_chapter_omitted_from_publication(tmp_path: Path) -> None:
    root, publisher, upstream, pdf = _fixture(tmp_path)
    artifacts = upstream["artifacts"]
    assert isinstance(artifacts, dict)
    omitted = b"declared upstream chapter\n"
    artifacts["upstream/root/chapters/omitted.qmd"] = {
        "sha256": _sha(omitted),
        "bytes": len(omitted),
    }

    with pytest.raises(ProjectionError, match="source chapter projection"):
        verify_projection(root, publisher, upstream, pdf)


def test_projection_rejects_claim_registry_or_pdf_mismatch(tmp_path: Path) -> None:
    root, publisher, upstream, pdf = _fixture(tmp_path)
    source = publisher["source"]
    assert isinstance(source, dict)
    claim_registry = source["claim_registry"]
    assert isinstance(claim_registry, dict)
    claim_registry["sha256"] = "0" * 64

    with pytest.raises(ProjectionError, match="claim registry"):
        verify_projection(root, publisher, upstream, pdf)

    claim_registry["sha256"] = _sha(b"claims")
    with pytest.raises(ProjectionError, match="publication.pdf"):
        verify_projection(root, publisher, upstream, b"different")


def test_checked_in_publication_projection_is_locked() -> None:
    publisher = json.loads((PUBLICATION_ROOT / "source_manifest.json").read_text(encoding="utf-8"))

    verify_projection_lock(PUBLICATION_ROOT, publisher)
