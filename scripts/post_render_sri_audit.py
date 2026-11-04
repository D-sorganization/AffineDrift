"""Post-render Subresource Integrity (SRI), third-party host, and ADR 0002 audit.

Issue #5252 (parent epic #5248): inventories every third-party script, stylesheet,
font, and preconnect host in rendered HTML output and template sources, verifies
whether external scripts/stylesheets carry valid SRI hashes (`sha256-`, `sha384-`,
`sha512-`), and fails when an external executable asset lacks `integrity`.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.cli_output import write_stderr, write_stdout

SRI_HASH_PATTERN = re.compile(r"^sha(?:256|384|512)-[A-Za-z0-9+/=]{32,}$")
DYNAMIC_SRC_PATTERN = re.compile(
    r'(\w+)\.src\s*=\s*["\'](https?://[^"\']+)["\']',
    re.DOTALL,
)
DYNAMIC_INTEGRITY_PATTERN = re.compile(
    r'(\w+)\.integrity\s*=\s*["\'](sha(?:256|384|512)-[^"\']+)["\']',
    re.DOTALL,
)

REPO_SCAN_PATHS: tuple[str, ...] = (
    "_includes/site-head.html",
    "_includes/mathjax-loader.html",
    "_templates/latex_article.html",
    "articles/rotation-converter.qmd",
    "src/tools/wrist_universal_joint/grip_angle_simulator.html",
)


@dataclass(frozen=True)
class ExternalAssetRecord:
    """Record describing an external asset or host reference in an HTML/QMD file."""

    source_file: str
    asset_type: str
    url: str
    host: str
    has_sri: bool
    sri_value: str
    crossorigin: str

    @property
    def requires_sri(self) -> bool:
        """Executable external scripts and stylesheets require SRI."""
        return self.asset_type in {"script", "stylesheet"}


class _ExternalAssetHTMLParser(HTMLParser):
    """HTML parser extracting external script, link, and inline dynamic script references."""

    def __init__(self, rel_path: str) -> None:
        super().__init__()
        self.rel_path = rel_path
        self.records: list[ExternalAssetRecord] = []
        self._in_script = False
        self._script_chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {k.lower(): (v or "") for k, v in attrs}
        if tag.lower() == "script":
            src = attr_map.get("src", "").strip()
            if src.startswith(("http://", "https://")):
                parsed = urlparse(src)
                integrity = attr_map.get("integrity", "").strip()
                self.records.append(
                    ExternalAssetRecord(
                        source_file=self.rel_path,
                        asset_type="script",
                        url=src,
                        host=parsed.netloc,
                        has_sri=bool(SRI_HASH_PATTERN.fullmatch(integrity)),
                        sri_value=integrity,
                        crossorigin=attr_map.get("crossorigin", "").strip(),
                    )
                )
            else:
                self._in_script = True
                self._script_chunks = []
        elif tag.lower() == "link":
            href = attr_map.get("href", "").strip()
            if not href.startswith(("http://", "https://")):
                return
            rel = attr_map.get("rel", "").strip().lower()
            if rel in {"stylesheet", "preload", "preconnect", "dns-prefetch"}:
                parsed = urlparse(href)
                integrity = attr_map.get("integrity", "").strip()
                self.records.append(
                    ExternalAssetRecord(
                        source_file=self.rel_path,
                        asset_type=rel,
                        url=href,
                        host=parsed.netloc,
                        has_sri=bool(SRI_HASH_PATTERN.fullmatch(integrity)),
                        sri_value=integrity,
                        crossorigin=attr_map.get("crossorigin", "").strip(),
                    )
                )

    def handle_data(self, data: str) -> None:
        if self._in_script:
            self._script_chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self._in_script:
            self._in_script = False
            script_body = "".join(self._script_chunks)
            integrity_by_var = {
                m.group(1): m.group(2) for m in DYNAMIC_INTEGRITY_PATTERN.finditer(script_body)
            }
            for match in DYNAMIC_SRC_PATTERN.finditer(script_body):
                var_name, url = match.groups()
                parsed = urlparse(url)
                integrity = integrity_by_var.get(var_name, "")
                self.records.append(
                    ExternalAssetRecord(
                        source_file=self.rel_path,
                        asset_type="script",
                        url=url,
                        host=parsed.netloc,
                        has_sri=bool(SRI_HASH_PATTERN.fullmatch(integrity)),
                        sri_value=integrity,
                        crossorigin="anonymous" if "crossOrigin" in script_body else "",
                    )
                )


def audit_html_file(file_path: Path, *, base_dir: Path | None = None) -> list[ExternalAssetRecord]:
    """Parse ``file_path`` and return all external asset records."""
    if not file_path.is_file():
        raise ValueError(f"HTML file does not exist: {file_path}")
    rel = (
        file_path.relative_to(base_dir).as_posix()
        if base_dir is not None and file_path.is_relative_to(base_dir)
        else file_path.as_posix()
    )
    parser = _ExternalAssetHTMLParser(rel)
    parser.feed(file_path.read_text(encoding="utf-8", errors="replace"))
    return parser.records


def audit_html_directory(site_dir: Path) -> list[ExternalAssetRecord]:
    """Audit all ``.html`` files under ``site_dir`` and return external asset records."""
    if not site_dir.exists() or not site_dir.is_dir():
        raise ValueError(f"Site directory does not exist: {site_dir}")

    records: list[ExternalAssetRecord] = []
    for html_path in sorted(site_dir.rglob("*.html")):
        records.extend(audit_html_file(html_path, base_dir=site_dir))
    return records


def collect_repo_third_party_inventory(repo_root: Path) -> list[ExternalAssetRecord]:
    """Collect third-party asset records across the canonical template and widget sources."""
    if not repo_root.exists() or not repo_root.is_dir():
        raise ValueError(f"Repository root does not exist: {repo_root}")

    records: list[ExternalAssetRecord] = []
    for rel_path in REPO_SCAN_PATHS:
        target = repo_root / rel_path
        if target.is_file():
            records.extend(audit_html_file(target, base_dir=repo_root))
    return records


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for post-render SRI verification."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--site-dir",
        type=Path,
        default=Path("_site"),
        help="Rendered HTML directory to audit",
    )
    args = parser.parse_args(argv)

    try:
        records = audit_html_directory(args.site_dir)
    except ValueError as exc:
        write_stderr(str(exc))
        return 2

    missing_sri = [rec for rec in records if rec.requires_sri and not rec.has_sri]
    if missing_sri:
        for rec in missing_sri:
            write_stderr(
                f"{rec.source_file}: external {rec.asset_type} {rec.url} missing valid SRI integrity attribute"
            )
        return 1

    write_stdout(
        f"Post-render SRI audit passed: {len(records)} external asset reference(s) verified."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
