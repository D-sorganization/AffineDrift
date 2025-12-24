import os
from bs4 import BeautifulSoup
from urllib.parse import urldefrag

DOCS_DIR = "docs"


def check_site_health() -> None:
    print(f"Scanning {DOCS_DIR} for HTML files...")

    html_files = []
    for root, _dirs, files in os.walk(DOCS_DIR):
        for file in files:
            if file.endswith(".html"):
                full_path = os.path.join(root, file)
                # Store relative path to docs/
                rel_path = os.path.relpath(full_path, DOCS_DIR)
                html_files.append(rel_path)

    print(f"Found {len(html_files)} HTML files.")

    # Store all known files (including assets if possible, but let's stick to HTML anchors first)
    # Actually, we should check if targets exist.
    # We need a set of all files in docs to verify links.
    all_files = set()
    for root, _dirs, files in os.walk(DOCS_DIR):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), DOCS_DIR)
            all_files.add(rel_path)

    # 1. Generate Site Map (List of pages)
    print("\n=== Site Map (Top Level) ===")
    top_level_pages = sorted([f for f in html_files if "/" not in f])
    for p in top_level_pages:
        print(f" - {p}")

    print("\n=== Site Map (Subdirectories) ===")
    subdirs = sorted(list(set([os.path.dirname(f) for f in html_files if "/" in f])))
    for d in subdirs:
        print(f"[{d}/]")
        pages = sorted(
            [os.path.basename(f) for f in html_files if os.path.dirname(f) == d]
        )
        for p in pages:
            print(f"   - {p}")

    # 2. Check Links
    print("\n=== Checking Links ===")
    broken_links = []
    orphaned_files = set(html_files)

    # Files that are always entry points (not orphaned)
    entry_points = {"index.html", "404.html"}
    orphaned_files -= entry_points

    for file_path in html_files:
        full_path = os.path.join(DOCS_DIR, file_path)
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")

            # Find all links
            for a in soup.find_all("a", href=True):
                href = a["href"]

                # Handle potential list/multi-valued attributes (though href should be string)
                if not isinstance(href, str):
                    continue

                # Skip external links, mailto, etc.
                if href.startswith(("http:", "https:", "mailto:", "tel:", "ftp:", "#")):
                    continue

                # Resolve relative links
                # href is relative to file_path
                # We need to construct the target path relative to DOCS_DIR

                # Strip anchor
                target_url, anchor = urldefrag(href)

                if not target_url:
                    # Pure anchor link to same page
                    continue

                # Calculate target path
                # If file_path is "articles/foo.html" and link is "../index.html"
                # dir is "articles"
                current_dir = os.path.dirname(file_path)
                target_rel_path = os.path.normpath(
                    os.path.join(current_dir, target_url)
                )

                # Check if file exists in all_files
                if target_rel_path not in all_files:
                    broken_links.append(
                        {
                            "source": file_path,
                            "target": target_rel_path,
                            "href": href,
                            "text": a.get_text(strip=True)[:50],
                        }
                    )
                else:
                    # Link is valid, remove target from orphaned list if it's an HTML file
                    if target_rel_path in orphaned_files:
                        orphaned_files.remove(target_rel_path)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    # Report Broken Links
    if broken_links:
        print(f"\nFound {len(broken_links)} broken internal links:")
        for link in broken_links:
            print(f"  [X] {link['source']} -> {link['href']} (Target: {link['target']})")
    else:
        print("\nNo broken internal links found.")

    # Report Orphaned Files
    if orphaned_files:
        print(
            f"\nFound {len(orphaned_files)} potentially orphaned HTML files (not linked from other internal pages):"
        )
        for orphaned in sorted(orphaned_files):
            print(f"  [?] {orphaned}")
    else:
        print("\nNo orphaned HTML files found.")


if __name__ == "__main__":
    check_site_health()
