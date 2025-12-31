import re
from pathlib import Path


def find_links(file_path: Path) -> list[tuple[str, int]]:
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Markdown links: [text](url)
    md_links = re.findall(r"\[.*?\]\((.*?)\)", content)

    # HTML links: href="url"
    html_links = re.findall(r'href=["\'](.*?)["\']', content)

    # Image links: src="url" (check for images too)
    img_links = re.findall(r'src=["\'](.*?)["\']', content)

    # Markdown images: ![text](url)
    md_imgs = re.findall(r"!\[.*?\]\((.*?)\)", content)

    all_links = md_links + html_links + img_links + md_imgs
    return [
        (link.strip(), i + 1)
        for i, line in enumerate(content.splitlines())
        for link in all_links
        if link in line
    ]  # Approximation of line number


def unique_broken(links: list[tuple[str, int, str]]) -> list[tuple[str, int, str]]:
    seen = set()
    unique = []
    for link in links:
        if link not in seen:
            unique.append(link)
            seen.add(link)
    return unique


def check_links(root_dir: str) -> list[tuple[str, int, str]]:
    root_path = Path(root_dir)
    broken_links: list[tuple[str, int, str]] = []

    print(f"Scanning {root_path}...")

    for file_path in root_path.rglob("*"):
        if (
            file_path.suffix not in [".qmd", ".html", ".md"]
            or "node_modules" in str(file_path)
            or "_site" in str(file_path)
            or ".git" in str(file_path)
            or "archive" in str(file_path)
            or "docs" in str(file_path)
            or "content" in str(file_path)
        ):
            continue

        try:
            links = find_links(file_path)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

        for link, line_num in links:
            # Clean link (remove fragments)
            url = link.split("#")[0]
            if not url:
                continue  # Just a fragment

            if url.startswith("http") or url.startswith("mailto:"):
                continue  # Skip external

            # Internal link
            # Check if absolute (relative to domain root) or relative
            if url.startswith("/"):
                # Assumes root_path is the site root
                target_path = root_path / url.lstrip("/")
            else:
                target_path = file_path.parent / url

            # Handle .html -> .qmd mapping
            # If linking to foo.html, it might come from foo.qmd
            if target_path.suffix == ".html":
                # Check for .html, .qmd, .md
                p_qmd = target_path.with_suffix(".qmd")
                p_md = target_path.with_suffix(".md")
                p_html = target_path  # The html itself might exist if it's a static asset

                # If target is generated from qmd, the source qmd should exist
                # But we are checking source files, so we look for source qmd
                if not (p_qmd.exists() or p_md.exists() or p_html.exists()):
                    # Also check if it wraps to index.html (e.g. directory/)
                    if not (target_path.is_dir() and (target_path / "index.qmd").exists()):
                        broken_links.append((str(file_path.relative_to(root_path)), line_num, link))
            else:
                if not target_path.exists():
                    broken_links.append((str(file_path.relative_to(root_path)), line_num, link))

    return unique_broken(broken_links)


if __name__ == "__main__":
    broken = check_links(".")
    if broken:
        print("\nBroken Links Found:")
        for file, line, link in broken:
            print(f"{file}:{line} -> {link}")
    else:
        print("\nNo broken internal links found.")
