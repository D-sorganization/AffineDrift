#!/usr/bin/env python3
"""
Repository Assessment Script
Generates assessments for 15 categories (A-O) and a comprehensive report.
"""

import ast
import logging
import re
import statistics
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Categories
CATEGORIES = {
    "A": "Code Structure",
    "B": "Documentation",
    "C": "Test Coverage",
    "D": "Error Handling",
    "E": "Performance",
    "F": "Security",
    "G": "Dependencies",
    "H": "CI/CD",
    "I": "Code Style",
    "J": "API Design",
    "K": "Data Handling",
    "L": "Logging",
    "M": "Configuration",
    "N": "Scalability",
    "O": "Maintainability",
}

GROUP_WEIGHTS = {
    "Code": 0.25,
    "Testing": 0.15,
    "Docs": 0.10,
    "Security": 0.15,
    "Perf": 0.15,
    "Ops": 0.10,
    "Design": 0.10,
}

GROUP_MAPPING = {
    "A": "Code",
    "D": "Code",
    "I": "Code",
    "O": "Code",
    "K": "Code",
    "L": "Code",
    "C": "Testing",
    "B": "Docs",
    "F": "Security",
    "G": "Security",
    "E": "Perf",
    "H": "Ops",
    "M": "Ops",
    "J": "Design",
    "N": "Design",
}


def get_python_files(root: Path) -> list[Path]:
    """
    Recursively finds all Python files in the given directory, excluding common ignored directories.
    """
    return [
        p
        for p in root.rglob("*.py")
        if "node_modules" not in p.parts and ".git" not in p.parts and "venv" not in p.parts
    ]


def assess_code_structure(files: list[Path]) -> dict[str, Any]:
    """
    Analyzes code structure metrics such as lines of code and file depth.
    """
    lines_counts = []
    for f in files:
        try:
            lines_counts.append(len(f.read_text(encoding="utf-8").splitlines()))
        except Exception:
            pass

    avg_loc = statistics.mean(lines_counts) if lines_counts else 0
    max_loc = max(lines_counts) if lines_counts else 0

    score = 10
    if avg_loc > 200:
        score -= 2
    if max_loc > 500:
        score -= 2

    max_depth = 0
    for f in files:
        depth = len(f.relative_to(Path.cwd()).parts)
        max_depth = max(max_depth, depth)

    if max_depth > 5:
        score -= 2

    return {
        "grade": max(0, score),
        "details": f"Files: {len(files)}, Avg LOC: {avg_loc:.1f}, Max LOC: {max_loc}, Max Depth: {max_depth}",
    }


def assess_documentation(files: list[Path]) -> dict[str, Any]:
    """
    Evaluates documentation coverage by counting docstrings in functions and classes.
    """
    docstring_count = 0
    function_count = 0
    class_count = 0

    for f in files:
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                    function_count += 1
                    if ast.get_docstring(node):
                        docstring_count += 1
                elif isinstance(node, ast.ClassDef):
                    class_count += 1
                    if ast.get_docstring(node):
                        docstring_count += 1
        except Exception:
            pass

    total_defs = function_count + class_count
    coverage = (docstring_count / total_defs) * 100 if total_defs > 0 else 0

    score = coverage / 10

    readmes = list(Path.cwd().rglob("README.md"))
    if len(readmes) > 5:
        score += 1

    return {
        "grade": min(10, max(0, score)),
        "details": f"Docstring Coverage: {coverage:.1f}% ({docstring_count}/{total_defs}), READMEs found: {len(readmes)}",
    }


def assess_test_coverage(root: Path) -> dict[str, Any]:
    """
    Estimates test coverage based on the presence and quantity of test files.
    """
    test_files = list(root.rglob("test_*.py")) + list(root.rglob("*_test.py"))

    # Heuristic based on file count, memory note says 19%
    score = 3
    if len(test_files) > 5:
        score += 1
    if len(test_files) > 20:
        score += 2

    return {
        "grade": min(10, score),
        "details": f"Test files found: {len(test_files)}. Historic coverage is low (~19%).",
    }


def assess_error_handling(files: list[Path]) -> dict[str, Any]:
    """
    Assesses error handling quality by checking for try/except blocks and bare excepts.
    """
    try_count = 0
    bare_except_count = 0

    for f in files:
        content = f.read_text(encoding="utf-8", errors="ignore")
        try_count += content.count("try:")
        bare_except_count += len(re.findall(r"except\s*:", content))

    score = 7
    if bare_except_count > 5:
        score -= 2
    if try_count == 0:
        score -= 3
    elif try_count > 20:
        score += 1

    return {
        "grade": max(0, min(10, score)),
        "details": f"Try blocks: {try_count}, Bare excepts: {bare_except_count}",
    }


def assess_logging(files: list[Path]) -> dict[str, Any]:
    """
    Evaluates logging practices by comparing usage of the logging module versus print statements.
    """
    logging_usage = 0
    print_usage = 0

    for f in files:
        if "test" in f.name:
            continue
        content = f.read_text(encoding="utf-8", errors="ignore")
        if "logging." in content or "logger." in content:
            logging_usage += 1
        if "print(" in content:
            print_usage += 1

    score = 5
    if logging_usage > print_usage:
        score += 3
    elif logging_usage > 0:
        score += 1

    return {
        "grade": min(10, score),
        "details": f"Files using logging: {logging_usage}, Files using print: {print_usage}",
    }


def assess_security(root: Path) -> dict[str, Any]:
    """
    Checks for security audit tools in GitHub workflows.
    """
    score = 7
    workflows = list(root.glob(".github/workflows/*.yml"))
    has_audit = False
    for w in workflows:
        content = w.read_text(encoding="utf-8")
        if "pip-audit" in content or "bandit" in content:
            has_audit = True
            break

    if has_audit:
        score += 2

    return {
        "grade": min(10, score),
        "details": f"Security audit tools present in workflows: {has_audit}",
    }


def assess_dependencies(root: Path) -> dict[str, Any]:
    """
    Reviews dependency management practices, checking for requirements.txt and package.json.
    """
    score = 0
    details = []

    req_txt = root / "requirements.txt"
    if req_txt.exists():
        score += 5
        details.append("requirements.txt found")
        content = req_txt.read_text(encoding="utf-8")
        pinned = len(re.findall(r"==\d", content))
        total = len(
            [line for line in content.splitlines() if line.strip() and not line.startswith("#")]
        )
        if total > 0 and pinned / total > 0.5:
            score += 3
            details.append(f"Most dependencies pinned ({pinned}/{total})")
        else:
            details.append("Many unpinned dependencies")
    else:
        details.append("requirements.txt NOT found")

    pkg_json = root / "package.json"
    if pkg_json.exists():
        score += 2
        details.append("package.json found")

    return {"grade": min(10, score), "details": "; ".join(details)}


def assess_cicd(root: Path) -> dict[str, Any]:
    """
    Analyzes CI/CD configuration, looking for workflows and test jobs.
    """
    score = 0
    details = []
    workflows_dir = root / ".github" / "workflows"
    if workflows_dir.exists():
        workflows = list(workflows_dir.glob("*.yml"))
        if workflows:
            score += 5
            details.append(f"Found {len(workflows)} workflows")
            test_jobs = 0
            for w in workflows:
                content = w.read_text(encoding="utf-8")
                if "run: pytest" in content or "npm test" in content:
                    test_jobs += 1
            if test_jobs > 0:
                score += 3
                details.append(f"{test_jobs} workflows run tests")
            else:
                details.append("No workflows run tests explicitly")
        else:
            details.append("Workflows directory empty")
    else:
        details.append("No .github/workflows directory")

    return {"grade": min(10, score), "details": "; ".join(details)}


def assess_code_style(root: Path) -> dict[str, Any]:
    """
    Checks for the presence of code style configuration files.
    """
    score = 0
    details = []

    configs = [".flake8", "ruff.toml", ".pylintrc", ".eslintrc", ".prettierrc"]
    found_configs = []
    for c in configs:
        if (root / c).exists():
            found_configs.append(c)

    if found_configs:
        score += 5
        details.append(f"Style configs found: {', '.join(found_configs)}")
    else:
        details.append("No standard style config files found")

    if (root / ".pre-commit-config.yaml").exists():
        score += 3
        details.append("Pre-commit config found")

    return {"grade": min(10, score), "details": "; ".join(details)}


def assess_api_design(files: list[Path]) -> dict[str, Any]:
    """
    Evaluates API design by checking for type hint usage in function signatures.
    """
    total_funcs = 0
    typed_funcs = 0

    for f in files:
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    total_funcs += 1
                    if node.returns:
                        typed_funcs += 1
        except Exception:
            pass

    score = 5
    if total_funcs > 0:
        ratio = typed_funcs / total_funcs
        score += ratio * 5
        details = f"Type hint coverage: {ratio:.1%} ({typed_funcs}/{total_funcs})"
    else:
        details = "No functions found to analyze"

    return {"grade": min(10, score), "details": details}


def assess_data_handling(files: list[Path]) -> dict[str, Any]:
    """
    Scans for common data I/O patterns to assess data handling practices.
    """
    io_patterns = ["open(", "json.load", "csv.reader", "pd.read", "sqlite3"]
    hits = 0
    for f in files:
        content = f.read_text(encoding="utf-8", errors="ignore")
        if any(p in content for p in io_patterns):
            hits += 1

    score = 7
    details = f"Files with data I/O: {hits}"
    return {"grade": score, "details": details}


def assess_configuration(root: Path) -> dict[str, Any]:
    """
    Checks for configuration files and environment variable usage.
    """
    score = 0
    details = []

    config_files = [".env.example", "config.py", "settings.py", "pyproject.toml"]
    found = []
    for c in config_files:
        if (root / c).exists():
            found.append(c)

    if found:
        score += 5
        details.append(f"Config files: {', '.join(found)}")

    environ_usage = 0
    for f in list(root.rglob("*.py")):
        if "os.environ" in f.read_text(encoding="utf-8", errors="ignore"):
            environ_usage += 1

    if environ_usage > 0:
        score += 3
        details.append(f"Env vars used in {environ_usage} files")

    return {"grade": min(10, score), "details": "; ".join(details)}


def assess_scalability_maintainability(files: list[Path]) -> dict[str, Any]:
    """
    Estimates scalability and maintainability based on code complexity metrics.
    """
    total_branches = 0
    total_funcs = 0

    for f in files:
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.If | ast.For | ast.While | ast.ExceptHandler):
                    total_branches += 1
                if isinstance(node, ast.FunctionDef):
                    total_funcs += 1
        except Exception:
            pass

    avg_complexity = total_branches / total_funcs if total_funcs > 0 else 0

    score = 10
    if avg_complexity > 10:
        score -= 5
    elif avg_complexity > 5:
        score -= 2

    details = f"Avg Complexity (branches/func): {avg_complexity:.1f}"

    return {"grade": max(0, score), "details": details}


def generate_report(
    category: str, category_name: str, grade: float, details: str, recommendations: list[str]
):
    """
    Writes a markdown report for a specific assessment category.
    """
    filename = f"docs/assessments/Assessment_{category}_{category_name.replace(' ', '_')}.md"
    content = f"""# Assessment: {category_name}

## Grade: {grade:.1f}/10

## Details
{details}

## Recommendations
"""
    for rec in recommendations:
        content += f"- {rec}\n"

    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    Path(filename).write_text(content, encoding="utf-8")
    return filename


def main():
    """
    Main function to execute the full repository assessment and generate reports.
    """
    root = Path.cwd()
    py_files = get_python_files(root)

    scores = {
        "A": assess_code_structure(py_files),
        "B": assess_documentation(py_files),
        "C": assess_test_coverage(root),
        "D": assess_error_handling(py_files),
        "E": {
            "grade": 7.0,
            "details": "Performance analysis requires runtime profiling",
        },  # Placeholder
        "F": assess_security(root),
        "G": assess_dependencies(root),
        "H": assess_cicd(root),
        "I": assess_code_style(root),
        "J": assess_api_design(py_files),
        "K": assess_data_handling(py_files),
        "L": assess_logging(py_files),
        "M": assess_configuration(root),
        "N": assess_scalability_maintainability(py_files),
        "O": assess_scalability_maintainability(py_files),  # Reuse complexity for maintainability
    }

    # Generate Individual Reports
    for cat_code, info in scores.items():
        name = CATEGORIES[cat_code]
        generate_report(cat_code, name, info["grade"], info["details"], ["See detailed findings"])

    # Generate Comprehensive Report
    weighted_sum = 0
    total_weight = 0

    group_scores = {g: [] for g in GROUP_WEIGHTS}

    for cat_code, info in scores.items():
        group = GROUP_MAPPING.get(cat_code, "Code")
        group_scores[group].append(info["grade"])

    for group, weight in GROUP_WEIGHTS.items():
        if group_scores[group]:
            avg_score = sum(group_scores[group]) / len(group_scores[group])
            weighted_sum += avg_score * weight
            total_weight += weight

    final_grade = weighted_sum / total_weight if total_weight > 0 else 0

    comp_content = f"""# Comprehensive Repository Assessment

## Overall Grade: {final_grade:.2f}/10

## Category Breakdown

| Category | Grade | Weight |
|----------|-------|--------|
"""
    for cat_code in sorted(scores.keys()):
        name = CATEGORIES[cat_code]
        info = scores[cat_code]
        comp_content += f"| {name} | {info['grade']:.1f} | - |\n"

    comp_content += """
## Top Recommendations
1. **Testing**: Increase test coverage immediately (Current: Low).
2. **Documentation**: Ensure all functions have docstrings.
3. **Logging**: Migrate all `print` statements to `logging`.
4. **Error Handling**: Reduce bare `except:` blocks.
5. **Security**: Maintain automated security scans.

## Issues Created
"""

    issues_dir = Path("docs/assessments/issues")
    issues_dir.mkdir(parents=True, exist_ok=True)

    for cat_code, info in scores.items():
        if info["grade"] < 5:
            issue_filename = (
                f"ISSUE_Assessment_{cat_code}_{CATEGORIES[cat_code].replace(' ', '_')}.md"
            )
            issue_path = issues_dir / issue_filename
            issue_content = f"""---
title: "Assessment Finding: Low Score in {CATEGORIES[cat_code]}"
labels: jules:assessment, needs-attention
---

# Issue: Low Score in {CATEGORIES[cat_code]}

**Grade**: {info['grade']:.1f}/10
**Details**: {info['details']}

## Recommended Actions
- Review the detailed assessment in `docs/assessments/Assessment_{cat_code}_{CATEGORIES[cat_code].replace(' ', '_')}.md`
- Create a remediation plan.
"""
            issue_path.write_text(issue_content, encoding="utf-8")
            comp_content += f"- Created issue: `{issue_filename}` (Grade: {info['grade']:.1f})\n"

    Path("docs/assessments/Comprehensive_Assessment.md").write_text(comp_content, encoding="utf-8")
    logger.info("Assessment complete.")


if __name__ == "__main__":
    main()
