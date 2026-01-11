#!/usr/bin/env python3
r"""
Scans Quarto markdown files (.qmd, .md) for common syntax issues that prevent
proper equation rendering.

Checks for:
1. LaTeX style delimiters: \(...\), \[...\] (recommends $...$ and $$...$$)
2. Spaces inside inline math: $ x $ (recommends $x$)
3. Double quotes inside math (recommends ' or '')
"""

import os
import re
import sys


def scan_file(filepath):
    issues = []
    try:
        with open(filepath, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []

    for i, line in enumerate(lines):
        line_num = i + 1

        # Skip code blocks
        if line.strip().startswith("```"):
            continue

        # 1. LaTeX delimiters
        if "\\(" in line or "\\)" in line:
            issues.append((line_num, line, "LaTeX inline \\( ... \\)", "Use $ ... $"))
        if "\\[" in line or "\\]" in line:
            # exclude \[1em] or similar spacing commands
            if not re.search(r"\\\[[\d\.]+[a-z]+\]", line):
                issues.append((line_num, line, "LaTeX display \\[ ... \\]", "Use $$ ... $$"))

        # 2. Math Spacing Check
        # Remove escaped \$
        clean_line = line.replace("\\$", "__")

        # Split by non-escaped $
        parts = re.split(r"(?<!\$)\$(?!\$)", clean_line)

        if len(parts) > 1:
            # We have potential inline math in odd indices
            for j in range(1, len(parts), 2):
                math_content = parts[j]
                if not math_content:
                    continue

                # Check for leading space
                if math_content.startswith(" ") or math_content.startswith("\t"):
                    issues.append(
                        (
                            line_num,
                            line,
                            f"Space after opening $ in segment '{math_content[:10]}...'",
                            "Remove leading space",
                        )
                    )

                # Check for trailing space
                if math_content.endswith(" ") or math_content.endswith("\t"):
                    issues.append(
                        (
                            line_num,
                            line,
                            f"Space before closing $ in segment '...{math_content[-10:]}'",
                            "Remove trailing space",
                        )
                    )

        # 3. Double quotes in math
        if len(parts) > 1:
            for j in range(1, len(parts), 2):
                math_content = parts[j]
                if '"' in math_content:
                    # Skip common HTML attributes in strings if they got caught
                    if "href=" in line or "src=" in line:
                        continue

                    issues.append(
                        (
                            line_num,
                            line,
                            f"Double quote in math: '{math_content}'",
                            "Use ' or '' for derivatives",
                        )
                    )

    return issues


def main():
    files_to_scan = []
    # Walk through articles
    if os.path.exists("articles"):
        for root, dirs, files in os.walk("articles"):
            if "archive" in dirs:
                dirs.remove("archive")
            for file in files:
                if file.endswith(".qmd") or file.endswith(".md"):
                    files_to_scan.append(os.path.join(root, file))

    # Walk through root
    for file in os.listdir("."):
        if file.endswith(".qmd"):
            files_to_scan.append(file)

    print(f"Scanning {len(files_to_scan)} active files for Quarto syntax issues...")

    total_issues = 0
    for filepath in files_to_scan:
        issues = scan_file(filepath)
        if issues:
            print(f"\nFile: {filepath}")
            for line_num, _line_content, problem, fix in issues:
                print(f"  Line {line_num}: {problem} -> {fix}")
            total_issues += len(issues)

    if total_issues > 0:
        print(f"\nTotal potential issues found: {total_issues}")
        sys.exit(1)
    else:
        print("\nNo issues found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
