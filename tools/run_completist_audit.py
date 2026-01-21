#!/usr/bin/env python3
import os
import re
import datetime
from pathlib import Path

# Configuration
EXCLUDE_DIRS = {
    '.git', 'node_modules', '__pycache__', '.jules', '.vscode',
    'assessments', 'site-packages', 'env', 'venv'
}
EXCLUDE_PATHS = {
    os.path.join('docs', 'assessments')
}
EXCLUDE_FILES = {
    'package-lock.json', 'yarn.lock', '.DS_Store',
    'run_completist_audit.py'
}
EXTENSIONS_TO_SCAN = {
    '.py', '.js', '.ts', '.qmd', '.md', '.html', '.css', '.yml', '.yaml'
}

# Regex Patterns
# Split strings to avoid self-detection
PATTERNS = {
    'TODO': re.compile(r'\bTO' + r'DO\b[:-]?(.*)', re.IGNORECASE),
    'FIXME': re.compile(r'\bFIX' + r'ME\b[:-]?(.*)', re.IGNORECASE),
    'HACK': re.compile(r'\bHA' + r'CK\b[:-]?(.*)', re.IGNORECASE),
    'TEMP': re.compile(r'\bTE' + r'MP\b[:-]?(.*)', re.IGNORECASE),
    'XXX': re.compile(r'\bXX' + r'X\b[:-]?(.*)', re.IGNORECASE),
    'NOT_IMPLEMENTED': re.compile(r'raise\s+NotImplementedError|NotImplementedError\(|^\s*pass\s*(#.*)?$'),
    'PLACEHOLDER': re.compile(r'(?i)(coming soon|under construction|placeholder|to be written|tbd)'),
}

# Reporting Structures
critical_incomplete = []
feature_gaps = []
content_gaps = []
technical_debt = []

def scan_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        rel_path = os.path.relpath(filepath, start=os.getcwd())
        ext = os.path.splitext(filepath)[1].lower()

        for i, line in enumerate(lines):
            line_num = i + 1
            stripped = line.strip()

            # Critical Incomplete
            # NotImplemented in code
            if ext in ['.py', '.js', '.ts']:
                if PATTERNS['NOT_IMPLEMENTED'].search(stripped):
                    # pass is tricky, let's include it if it's the only thing in a block or marked
                    if 'pass' in stripped and not 'TODO' in stripped:
                         # Maybe too broad, but let's log it as feature gap unless explicit error
                         feature_gaps.append({'file': rel_path, 'line': line_num, 'content': stripped, 'type': 'Partial Implementation'})
                    elif 'NotImplementedError' in stripped:
                         critical_incomplete.append({'file': rel_path, 'line': line_num, 'content': stripped, 'type': 'NotImplementedError'})

            # Content Gaps / Critical (if user facing)
            if ext in ['.qmd', '.md', '.html']:
                if PATTERNS['PLACEHOLDER'].search(stripped):
                    msg = PATTERNS['PLACEHOLDER'].search(stripped).group(0)
                    item = {'file': rel_path, 'line': line_num, 'content': stripped, 'type': f'Placeholder ({msg})'}

                    # If it's a main page, it's Critical
                    if rel_path in ['index.qmd', 'tools.qmd', 'about.qmd', 'contact.qmd']:
                        critical_incomplete.append(item)
                    else:
                        content_gaps.append(item)

            # Feature Gaps
            if PATTERNS['TODO'].search(stripped):
                match = PATTERNS['TODO'].search(stripped)
                feature_gaps.append({'file': rel_path, 'line': line_num, 'content': match.group(0), 'type': 'TODO'})

            # Technical Debt
            if PATTERNS['FIXME'].search(stripped):
                match = PATTERNS['FIXME'].search(stripped)
                technical_debt.append({'file': rel_path, 'line': line_num, 'content': match.group(0), 'type': 'FIXME'})
            if PATTERNS['HACK'].search(stripped):
                match = PATTERNS['HACK'].search(stripped)
                technical_debt.append({'file': rel_path, 'line': line_num, 'content': match.group(0), 'type': 'HACK'})
            if PATTERNS['TEMP'].search(stripped):
                match = PATTERNS['TEMP'].search(stripped)
                technical_debt.append({'file': rel_path, 'line': line_num, 'content': match.group(0), 'type': 'TEMP'})
            if PATTERNS['XXX'].search(stripped):
                match = PATTERNS['XXX'].search(stripped)
                technical_debt.append({'file': rel_path, 'line': line_num, 'content': match.group(0), 'type': 'XXX'})

    except Exception as e:
        print(f"Error scanning {filepath}: {e}")

def main():
    root_dir = os.getcwd()

    for root, dirs, files in os.walk(root_dir):
        # Modify dirs in-place to skip excluded
        # Filter by directory name
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        # Filter by full path (relative to root)
        dirs[:] = [d for d in dirs if os.path.relpath(os.path.join(root, d), root_dir) not in EXCLUDE_PATHS]

        for file in files:
            if file in EXCLUDE_FILES:
                continue

            ext = os.path.splitext(file)[1].lower()
            if ext in EXTENSIONS_TO_SCAN:
                filepath = os.path.join(root, file)
                scan_file(filepath)

    # Generate Report
    generate_report()

def generate_report():
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    report_filename = f"docs/assessments/completist/Completist_Report_{date_str}.md"
    latest_filename = "docs/assessments/completist/COMPLETIST_LATEST.md"

    os.makedirs("docs/assessments/completist", exist_ok=True)
    os.makedirs("docs/assessments/issues", exist_ok=True)

    report_content = f"""# Completist Report - {date_str}

## Executive Summary
- **Critical Incomplete Items:** {len(critical_incomplete)}
- **Feature Gaps:** {len(feature_gaps)}
- **Content Gaps:** {len(content_gaps)}
- **Technical Debt Items:** {len(technical_debt)}

## 1. Critical Incomplete (Blocking)
"""
    if critical_incomplete:
        for item in critical_incomplete:
            report_content += f"- **{item['type']}** in `{item['file']}:{item['line']}`: {item['content'].strip()}\n"
    else:
        report_content += "- None detected.\n"

    report_content += "\n## 2. Feature Gaps\n"
    if feature_gaps:
        # Group by file? Or list all? Listing all for now.
        for item in feature_gaps:
             report_content += f"- **{item['type']}** in `{item['file']}:{item['line']}`: {item['content'].strip()}\n"
    else:
        report_content += "- None detected.\n"

    report_content += "\n## 3. Content Gaps (Website Specific)\n"
    if content_gaps:
        for item in content_gaps:
            report_content += f"- **{item['type']}** in `{item['file']}:{item['line']}`: {item['content'].strip()}\n"
    else:
        report_content += "- None detected.\n"

    report_content += "\n## 4. Technical Debt\n"
    if technical_debt:
        for item in technical_debt:
            report_content += f"- **{item['type']}** in `{item['file']}:{item['line']}`: {item['content'].strip()}\n"
    else:
        report_content += "- None detected.\n"

    # Write Report
    with open(report_filename, 'w') as f:
        f.write(report_content)

    # Update Latest
    with open(latest_filename, 'w') as f:
        f.write(report_content)

    print(f"Reports generated: {report_filename}, {latest_filename}")

    # Handle Critical Issues
    if critical_incomplete:
        issue_log_path = "docs/assessments/issues/ISSUE_CREATION_LOG.md"
        with open(issue_log_path, 'a') as f:
            f.write(f"\n\n## Completist Audit {date_str}\n")
            for item in critical_incomplete:
                f.write(f"- [CRITICAL] {item['type']} in {item['file']}\n")
                f.write(f"  - Context: {item['content'].strip()}\n")
                f.write(f"  - Action: Create GitHub Issue labeled 'incomplete-implementation,critical'\n")

if __name__ == "__main__":
    main()
