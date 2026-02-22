import re
from pathlib import Path


def finalize():
    comp_path = Path("docs/assessments/Comprehensive_Assessment.md")
    completist_path = Path("docs/assessments/Assessment_Completist.md")
    pragmatic_path = Path("docs/assessments/Assessment_Pragmatic_Programmer.md")

    if not comp_path.exists():
        print("Comprehensive Assessment not found.")
        return

    content = comp_path.read_text(encoding="utf-8")

    # Append Extended Assessments Section
    content += "\n\n# Extended Assessments\n"

    # Completist Summary
    if completist_path.exists():
        completist_content = completist_path.read_text(encoding="utf-8")
        match = re.search(r"## Executive Summary(.*?)(##|\Z)", completist_content, re.DOTALL)
        if match:
            content += "\n## Completist Audit Summary\n"
            content += match.group(1).strip() + "\n"
            content += "\n[Full Completist Report](Assessment_Completist.md)\n"

    # Pragmatic Summary
    if pragmatic_path.exists():
        pragmatic_content = pragmatic_path.read_text(encoding="utf-8")
        findings_match = re.search(r"## Findings(.*?)(##|\Z)", pragmatic_content, re.DOTALL)
        if findings_match:
            findings = findings_match.group(1).strip()
            # Count issues
            issue_count = findings.count("- **")
            content += "\n## Pragmatic Programmer Review Summary\n"
            content += f"- **Total Issues Found**: {issue_count}\n"
            # Maybe show top 10 lines?
            lines = findings.splitlines()
            if lines:
                preview = "\n".join(lines[:15])
                content += f"\n### Preview\n{preview}\n..."
            content += (
                "\n\n[Full Pragmatic Programmer Review](Assessment_Pragmatic_Programmer.md)\n"
            )

    comp_path.write_text(content, encoding="utf-8")
    print("Updated Comprehensive Assessment.")


if __name__ == "__main__":
    finalize()
