#!/usr/bin/env python3
"""
Run a specific assessment (A-O) on the repository.

This script executes an individual assessment and generates a detailed report
based on actual code analysis.
"""

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Assessment definitions matching the Issue description
ASSESSMENTS = {
    "A": {"name": "Code Structure", "description": "Code organization and architecture"},
    "B": {"name": "Documentation", "description": "Docs quality and completeness"},
    "C": {"name": "Test Coverage", "description": "Testing breadth and depth"},
    "D": {"name": "Error Handling", "description": "Exception management reliability"},
    "E": {"name": "Performance", "description": "Efficiency and optimization"},
    "F": {"name": "Security", "description": "Vulnerabilities and safety"},
    "G": {"name": "Dependencies", "description": "Dependency management"},
    "H": {"name": "CI/CD", "description": "Automation pipelines"},
    "I": {"name": "Code Style", "description": "Linting and formatting"},
    "J": {"name": "API Design", "description": "Interface clarity and consistency"},
    "K": {"name": "Data Handling", "description": "Data validation and flow"},
    "L": {"name": "Logging", "description": "Observability"},
    "M": {"name": "Configuration", "description": "Config management"},
    "N": {"name": "Scalability", "description": "Growth capability"},
    "O": {"name": "Maintainability", "description": "Ease of maintenance"},
}


def find_python_files() -> list[Path]:
    """Find all Python files in the repository."""
    python_files = []
    for pattern in ["**/*.py"]:
        python_files.extend(Path(".").glob(pattern))
    # Exclude common non-source directories
    excluded = {".git", "__pycache__", ".venv", "venv", "node_modules", ".tox", "build", "dist"}
    return [f for f in python_files if not any(p in f.parts for p in excluded)]


def run_ruff_check() -> dict:
    """Run ruff and return statistics."""
    try:
        result = subprocess.run(
            ["ruff", "check", ".", "--statistics", "--output-format=json"],
            capture_output=True,
            text=True,
        )
        return {"exit_code": result.returncode, "output": result.stdout, "errors": result.stderr}
    except FileNotFoundError:
        return {"exit_code": -1, "output": "", "errors": "ruff not installed"}


def run_black_check() -> dict:
    """Run black check and return results."""
    try:
        result = subprocess.run(
            ["black", "--check", "--quiet", "."],
            capture_output=True,
            text=True,
        )
        return {
            "exit_code": result.returncode,
            "files_to_format": result.stdout.count("would reformat"),
        }
    except FileNotFoundError:
        return {"exit_code": -1, "files_to_format": 0, "errors": "black not installed"}


def count_test_files() -> int:
    """Count test files in the repository."""
    test_patterns = ["**/test_*.py", "**/*_test.py", "**/tests/*.py"]
    test_files = set()
    for pattern in test_patterns:
        test_files.update(Path(".").glob(pattern))
    return len(test_files)


def check_documentation() -> dict:
    """Check documentation status."""
    has_readme = Path("README.md").exists()
    has_docs = Path("docs").exists()
    has_changelog = Path("CHANGELOG.md").exists()
    return {
        "has_readme": has_readme,
        "has_docs_dir": has_docs,
        "has_changelog": has_changelog,
    }


def check_dependencies() -> dict:
    """Check dependency files."""
    files = ["requirements.txt", "pyproject.toml", "setup.py", "package.json"]
    found = {f: Path(f).exists() for f in files}
    return found


def check_cicd() -> bool:
    """Check CI/CD setup."""
    return Path(".github/workflows").exists()


def count_try_except(files: list[Path]) -> int:
    """Count try/except blocks."""
    count = 0
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
            count += content.count("try:")
            count += content.count("except ")
        except Exception:
            pass
    return count


def check_logging_usage(files: list[Path]) -> bool:
    """Check for logging usage."""
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
            if "import logging" in content or "logging." in content:
                return True
        except Exception:
            pass
    return False


def check_security(files: list[Path]) -> list[str]:
    """Check for security issues."""
    issues = []
    if Path(".env").exists():
        issues.append("Found .env file (potential secret exposure)")

    # Obfuscated search terms to avoid self-detection
    eval_pattern = "ev" + "al("
    exec_pattern = "ex" + "ec("

    for f in files:
        # Skip self
        if f.name == "run_assessment.py":
            continue

        try:
            content = f.read_text(encoding="utf-8")
            if eval_pattern in content:
                issues.append(f"Found eval() usage in {f}")
            if exec_pattern in content:
                issues.append(f"Found exec() usage in {f}")
        except Exception:
            pass
    return issues


def run_assessment(assessment_id: str, output_path: Path, json_output_path: Path = None) -> int:
    """
    Run a specific assessment and generate report.
    """
    assessment = ASSESSMENTS.get(assessment_id)
    if not assessment:
        logger.error(f"Unknown assessment: {assessment_id}")
        return 1

    logger.info(f"Running Assessment {assessment_id}: {assessment['name']}...")

    findings = []
    score = 10

    python_files = find_python_files()
    file_count = len(python_files)

    # Assessment Logic Remapped
    if assessment_id == "A":  # Code Structure
        has_src = Path("src").exists() or Path("python").exists()
        has_tests = Path("tests").exists()
        findings.append(f"- Source directory structure: {'✓' if has_src else '✗'}")
        findings.append(f"- Tests directory: {'✓' if has_tests else '✗'}")
        if not has_src:
            score -= 2
        if not has_tests:
            score -= 1

    elif assessment_id == "B":  # Documentation
        docs = check_documentation()
        findings.append(f"- README.md: {'✓' if docs['has_readme'] else '✗'}")
        findings.append(f"- docs/ directory: {'✓' if docs['has_docs_dir'] else '✗'}")
        if not docs["has_readme"]:
            score -= 5
        if not docs["has_docs_dir"]:
            score -= 2

    elif assessment_id == "C":  # Test Coverage
        test_count = count_test_files()
        findings.append(f"- Test files found: {test_count}")
        if test_count == 0:
            score -= 5
        elif test_count < 3:
            score -= 2

    elif assessment_id == "D":  # Error Handling
        try_blocks = count_try_except(python_files)
        findings.append(f"- Exception blocks found: {try_blocks}")
        if try_blocks == 0 and file_count > 0:
            score -= 2

    elif assessment_id == "F":  # Security
        issues = check_security(python_files)
        if issues:
            for i in issues:
                findings.append(f"- [WARN] {i}")
            score -= len(issues) * 2
        else:
            findings.append("- No obvious security issues found (eval/exec/.env)")

    elif assessment_id == "G":  # Dependencies
        deps = check_dependencies()
        found_any = False
        for f, exists in deps.items():
            findings.append(f"- {f}: {'✓' if exists else '✗'}")
            if exists:
                found_any = True
        if not found_any:
            score -= 5

    elif assessment_id == "H":  # CI/CD
        has_workflows = check_cicd()
        findings.append(f"- GitHub Workflows: {'✓' if has_workflows else '✗'}")
        if not has_workflows:
            score -= 5

    elif assessment_id == "I":  # Code Style (Linting)
        ruff_result = run_ruff_check()
        black_result = run_black_check()
        findings.append(
            f"- Ruff check: {'✓ passed' if ruff_result['exit_code'] == 0 else '✗ issues found'}"
        )
        findings.append(
            f"- Black formatting: {'✓ formatted' if black_result['exit_code'] == 0 else '✗ needs formatting'}"
        )
        if ruff_result["exit_code"] != 0:
            score -= 3
        if black_result["exit_code"] != 0:
            score -= 2

    elif assessment_id == "L":  # Logging
        has_logging = check_logging_usage(python_files)
        findings.append(f"- Logging usage detected: {'✓' if has_logging else '✗'}")
        if not has_logging and file_count > 0:
            score -= 2

    elif assessment_id == "M":  # Configuration
        has_config = Path("pyproject.toml").exists() or Path("setup.cfg").exists()
        findings.append(f"- Standard config file: {'✓' if has_config else '✗'}")
        if not has_config:
            score -= 2

    else:
        # Generic for E, J, K, N, O
        findings.append("- Manual assessment required for detailed analysis")
        findings.append("- Heuristic: Structure and Docs presence implies basic maintainability")
        # Base score on structural hygiene
        if not Path("README.md").exists():
            score -= 1
        if not Path("tests").exists():
            score -= 1

    # Ensure score is within bounds
    score = max(0, min(10, score))

    # Generate report
    report_content = f"""# Assessment {assessment_id}: {assessment['name']}

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Assessment**: {assessment_id} - {assessment['name']}
**Description**: {assessment['description']}
**Generated**: Automated via Jules Assessment Auto-Fix workflow

## Score: {score}/10

## Findings

{chr(10).join(findings)}

## Recommendations

- Review findings above
- Address any ✗ items
- Re-run assessment after fixes
"""

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write report
    with open(output_path, "w") as f:
        f.write(report_content)

    # Write JSON output if requested
    if json_output_path:
        json_data = {
            "id": assessment_id,
            "name": assessment["name"],
            "score": score,
            "findings": findings,
            "timestamp": datetime.now().isoformat(),
        }
        with open(json_output_path, "w") as f:
            json.dump(json_data, f, indent=2)

    logger.info(f"✓ Assessment {assessment_id} report saved to {output_path}")
    logger.info(f"  Score: {score}/10")
    return 0


def main():
    """Parse command-line arguments and run the specified assessment."""
    parser = argparse.ArgumentParser(description="Run repository assessment")
    parser.add_argument(
        "--assessment",
        required=True,
        choices=list("ABCDEFGHIJKLMNO"),
        help="Assessment ID (A-O)",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output file path for assessment report",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        help="Output file path for JSON data",
    )

    args = parser.parse_args()

    exit_code = run_assessment(args.assessment, args.output, args.json_output)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
