#!/usr/bin/env python3
"""Verify image URLs in markdown and HTML files."""

import re
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def extract_image_urls(content: str) -> list[str]:
    """Extract all image URLs from markdown and HTML content.

    Args:
        content: The file content to search for image URLs.

    Returns:
        A list of image URLs found in the content.
    """
    # Match HTML img tags
    html_matches = re.findall(r'<img\s+[^>]*src=["\']([^"\']+)["\']', content)

    # Match Markdown images
    md_matches = re.findall(r"!\[.*?\]\((.*?)\)", content)

    return html_matches + md_matches


def check_url(url: str, file_path: Path) -> str | None:
    """Check if a URL is accessible.

    Args:
        url: The URL to check.
        file_path: Path to the file containing the URL.

    Returns:
        None if the URL is valid, otherwise a string describing the error.
    """
    if url.startswith("http"):
        try:
            req = urllib.request.Request(url, method="HEAD")
            # Add a user agent to avoid 403s from some sites
            req.add_header(
                "User-Agent",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status >= 400:
                    return f"BROKEN (External): {url} in {file_path} (Status: {response.status})"
                return None
        except urllib.error.HTTPError as e:
            return f"BROKEN (External): {url} in {file_path} (Status: {e.code})"
        except Exception as e:
            return f"BROKEN (External): {url} in {file_path} (Error: {e})"
    else:
        # Local file
        # Handle relative paths
        if url.startswith("/"):
            # Absolute path relative to site root? Or system root?
            # Usually / starts from root of website.
            local_path = Path(".") / url.lstrip("/")
        else:
            # Relative to the file
            local_path = Path(file_path).parent / url

        if not local_path.exists():
            # Try checking relative to root if above fails (common in some SSGs)
            root_path = Path(".") / url
            if root_path.exists():
                return None  # It exists relative to root

            return (
                f"BROKEN (Local): {url} in {file_path} (Resolved to: {local_path} or {root_path})"
            )
        return None


def process_file(file_path: Path) -> list[str]:
    """Process a file and check all image URLs.

    Args:
        file_path: Path to the file to process.

    Returns:
        A list of error messages for broken image URLs found in the file.
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    urls = extract_image_urls(content)
    results = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(check_url, url, file_path): url for url in urls}
        for future in futures:
            result = future.result()
            if result:
                results.append(result)

    return results


def main() -> None:
    """Main function to verify images in all relevant files."""
    files = list(Path(".").rglob("*.qmd")) + list(Path(".").rglob("*.html"))
    # Filter out _site or docs if we are checking source
    files = [f for f in files if "_site" not in str(f) and "docs" not in str(f)]

    all_broken = []

    print(f"Checking {len(files)} files...")

    for file_path in files:
        # print(f"Scanning {file_path}...")
        broken = process_file(file_path)
        if broken:
            all_broken.extend(broken)
            for b in broken:
                print(b)

    if not all_broken:
        print("No broken images found!")
    else:
        print(f"Found {len(all_broken)} broken image references.")


if __name__ == "__main__":
    main()
