"""Keep pages/upstreamdrift-conventions.qmd aligned with canonical-v2 at the pin (#5619)."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
from dataclasses import dataclass
from pathlib import Path

from scripts.pinned_https import GITHUB_RAW_HOST, read_pinned_https, require_commit_sha

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONTRACT = ROOT / "data/upstreamdrift/canonical_v2_page_contract.json"
RAW_DOC = f"https://{GITHUB_RAW_HOST}/D-sorganization/UpstreamDrift/{{commit}}/{{doc_path}}"


@dataclass(frozen=True)
class PageContract:
    """Pinned UpstreamDrift canonical-v2 strings mirrored on the AffineDrift page."""

    upstream_commit: str
    upstream_doc: str
    page_path: Path
    upstream_required: tuple[str, ...]
    page_required: tuple[str, ...]


def load_contract(path: Path) -> PageContract:
    """Load and validate the JSON contract."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    schema = payload.get("schema_version")
    if schema != "affinedrift/upstreamdrift-canonical-v2-page-contract/v1":
        raise ValueError(f"unexpected schema in {path}: {schema!r}")
    commit = str(payload["upstream_commit"])
    require_commit_sha(commit)
    page_rel = str(payload["page_path"])
    return PageContract(
        upstream_commit=commit,
        upstream_doc=str(payload["upstream_doc"]),
        page_path=Path(page_rel),
        upstream_required=_string_tuple(
            payload.get("upstream_required_substrings"), "upstream_required_substrings"
        ),
        page_required=_string_tuple(
            payload.get("page_required_substrings"), "page_required_substrings"
        ),
    )


def _string_tuple(values: object, field: str) -> tuple[str, ...]:
    if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
        raise ValueError(f"{field} must be a list of strings")
    return tuple(values)


def fetch_canonical_v2(contract: PageContract) -> str:
    """Return UpstreamDrift canonical-v2.md at the pinned commit."""
    url = RAW_DOC.format(commit=contract.upstream_commit, doc_path=contract.upstream_doc)
    try:
        return read_pinned_https(url, host=GITHUB_RAW_HOST).decode("utf-8")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"failed to fetch {contract.upstream_doc}: {exc}") from exc


def _missing(text: str, needles: tuple[str, ...], label: str) -> list[str]:
    return [
        f"{label} missing required substring: {needle!r}"
        for needle in needles
        if needle not in text
    ]


def check_upstream_doc(text: str, contract: PageContract) -> list[str]:
    """Verify the pinned upstream doc still carries the contracted anchors."""
    return _missing(text, contract.upstream_required, "upstream canonical-v2.md")


def check_page(text: str, contract: PageContract) -> list[str]:
    """Verify the AffineDrift conventions page still mirrors the contract."""
    return _missing(text, contract.page_required, contract.page_path.as_posix())


def run_check(contract_path: Path, repo_root: Path) -> list[str]:
    """Fetch upstream text, read the page, and return all violations."""
    contract = load_contract(contract_path)
    page_file = repo_root / contract.page_path
    if not page_file.is_file():
        return [f"missing page file: {contract.page_path}"]
    page_text = page_file.read_text(encoding="utf-8")
    errors = check_upstream_doc(fetch_canonical_v2(contract), contract)
    errors.extend(check_page(page_text, contract))
    return errors


def main(argv: list[str] | None = None) -> int:
    """CLI entry: exit 1 when the page drifts from canonical-v2 at the pin."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--contract",
        type=Path,
        default=DEFAULT_CONTRACT,
        help="path to canonical_v2_page_contract.json",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="repository root (for tests)",
    )
    args = parser.parse_args(argv)
    errors = run_check(args.contract, args.root)
    if errors:
        for line in errors:
            print(line, file=sys.stderr)
        return 1
    commit = load_contract(args.contract).upstream_commit
    print(f"OK: {args.contract.name} satisfied at UpstreamDrift {commit[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
