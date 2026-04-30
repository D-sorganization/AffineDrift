#!/usr/bin/env python3
"""
Link Checker: Validate Quarto references and external URLs in markdown files.

Validates:
- Quarto internal references (@sec-, @fig-, @eq-)
- External HTTP/HTTPS URLs (with retry logic)
- Configurable allowlists and timeouts

Exit codes:
  0: All checks passed
  1: Critical errors (internal references)
  2: Warnings (external URL failures with retries)
"""

import argparse
import re
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

# Configuration
INTERNAL_REF_PATTERN = r"@(sec|fig|eq|tbl|lst|exr)-[\w-]+"
EXTERNAL_URL_PATTERN = r"https?://[^\s\)\]\}]+"
KNOWN_FRAGILE_URLS = {
    "github.com",
    "arxiv.org",
    "stackoverflow.com",
}
TIMEOUT = 5
MAX_RETRIES = 2
RETRY_DELAY = 1


def find_markdown_files(root_dir: str) -> list[Path]:
    """Find all markdown and qmd files, excluding cache and environment directories."""
    files = []
    ignore_dirs = {".pytest_cache", ".venv", ".ruff_cache", "node_modules", ".git"}

    root_path = Path(root_dir)
    for pattern in ["**/*.md", "**/*.qmd"]:
        for path in root_path.glob(pattern):
            if not any(part in ignore_dirs for part in path.parts):
                files.append(path)
    return files


def extract_internal_refs(content: str) -> set[str]:
    """Extract Quarto internal references (@sec-, @fig-, etc)."""
    matches = re.findall(INTERNAL_REF_PATTERN, content)
    return set(matches)


def extract_external_urls(content: str) -> set[str]:
    """Extract external URLs from content."""
    matches = re.findall(EXTERNAL_URL_PATTERN, content)
    # Clean up URLs (remove trailing punctuation)
    urls = set()
    for url in matches:
        url = url.rstrip(".,;:!?'\")")

        if (
            url.startswith("http://localhost")
            or url.endswith(".git")
            or url.endswith(".git`")
            or "github.com" in url
        ):
            continue

        if url.startswith("http"):
            urls.add(url)
    return urls


def find_ref_definitions(root_dir: str) -> set[str]:
    """Find all defined Quarto references (labels)."""
    defined_refs = set()
    for file_path in find_markdown_files(root_dir):
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
                # Look for {#sec-xxx} or {#fig-xxx} patterns (label definitions)
                labels = re.findall(r"\{#(sec|fig|eq|tbl|lst|exr)-[\w-]+\}", content)
                defined_refs.update(labels)
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)
    return defined_refs


def validate_url(url: str, retries: int = MAX_RETRIES) -> tuple[bool, str]:  # noqa: C901
    """Validate URL with retry logic."""
    domain = urlparse(url).netloc

    # Fragile URLs get more lenient handling
    is_fragile = any(d in domain for d in KNOWN_FRAGILE_URLS)

    for attempt in range(retries):
        try:
            req = Request(url, headers={"User-Agent": "Link-Checker/1.0"})  # noqa: S310
            with urlopen(req, timeout=TIMEOUT) as response:  # noqa: S310
                if response.status < 400:
                    return True, f"OK ({response.status})"
                elif response.status < 500:
                    return False, f"Client error ({response.status})"
                else:
                    if attempt < retries - 1:
                        time.sleep(RETRY_DELAY)
                        continue
                    return not is_fragile, f"Server error ({response.status})"
        except HTTPError as e:
            if e.code < 500:
                return False, f"HTTP {e.code}"
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY)
                continue
            return not is_fragile, f"HTTP {e.code} (after {retries} retries)"
        except (URLError, TimeoutError) as e:
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY)
                continue
            return not is_fragile, f"Connection error: {str(e)[:50]}"
        except Exception as e:
            return False, f"Error: {str(e)[:50]}"

    return False, "Max retries exceeded"


def check_file(
    file_path: Path, defined_refs: set[str], external_only: bool = False
) -> tuple[list[str], list[str]]:
    """Check a single file for broken references and URLs."""
    errors = []
    warnings = []

    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Check internal references
        if not external_only:
            refs_used = extract_internal_refs(content)
            for ref in refs_used:
                if ref not in defined_refs:
                    errors.append(f"{file_path}: Undefined reference: @{ref}")

        # Check external URLs
        urls = extract_external_urls(content)
        for url in urls:
            is_valid, reason = validate_url(url)
            if not is_valid:
                warnings.append(f"{file_path}: Invalid URL: {url} ({reason})")

    except Exception as e:
        errors.append(f"{file_path}: Error reading file: {e}")

    return errors, warnings


def main():  # noqa: C901
    parser = argparse.ArgumentParser(description="Validate Quarto references and URLs")
    parser.add_argument("--root", default=".", help="Root directory to check")
    parser.add_argument("--external-only", action="store_true", help="Only check external URLs")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--file", help="Check specific file")
    args = parser.parse_args()

    root_dir = args.root

    if args.verbose:
        print(f"Scanning {root_dir}...", file=sys.stderr)

    # Find all markdown files
    files = [Path(args.file)] if args.file else find_markdown_files(root_dir)
    if args.verbose:
        print(f"Found {len(files)} markdown files", file=sys.stderr)

    # Find all defined references
    defined_refs = set() if args.external_only else find_ref_definitions(root_dir)
    if args.verbose and defined_refs:
        print(f"Found {len(defined_refs)} defined references", file=sys.stderr)

    # Check all files
    all_errors = []
    all_warnings = []

    for file_path in files:
        errors, warnings = check_file(file_path, defined_refs, args.external_only)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    # Report results
    if all_errors:
        print("ERRORS (critical):", file=sys.stderr)
        for error in all_errors:
            print(f"  ✗ {error}")

    if all_warnings:
        print("WARNINGS (non-critical):", file=sys.stderr)
        for warning in all_warnings[:10]:  # Limit to first 10
            print(f"  ⚠ {warning}")
        if len(all_warnings) > 10:
            print(f"  ... and {len(all_warnings) - 10} more warnings")

    if not all_errors and not all_warnings:
        print("✓ All links valid!")
        return 0

    if all_errors:
        print(f"\n✗ {len(all_errors)} critical errors", file=sys.stderr)
        return 1

    if all_warnings:
        print(f"\n⚠ {len(all_warnings)} warnings (external URLs)", file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
