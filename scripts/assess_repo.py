#!/usr/bin/env python3
"""
Repository Assessment Script
Generates assessments for 15 categories (A-O) and a comprehensive report.
"""

import re
import statistics
import sys
from pathlib import Path
from typing import Any

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parents[1]))

from src.tools.utils import (
    get_python_files,
    setup_logging,
)
from src.tools.utils.analysis_utils import (
    assess_error_handling_content,
    assess_logging_content,
    calculate_complexity,
    get_python_metrics,
)
from src.tools.utils.assessment_utils import (
    CATEGORIES,
    GROUP_MAPPING,
    GROUP_WEIGHTS,
)
from src.tools.utils.report_utils import (
    generate_issue_document,
    generate_markdown_report,
)

logger = setup_logging(__name__, format_string="%(message)s")


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
    total_defs = 0

    for f in files:
        metrics = get_python_metrics(f)
        docstring_count += metrics["docstrings"]
        total_defs += metrics["functions"] + metrics["classes"]

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
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            results = assess_error_handling_content(content)
            try_count += results["try_count"]
            bare_except_count += results["bare_except_count"]
        except Exception:
            pass

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
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            results = assess_logging_content(content)
            logging_usage += results["logging_usage"]
            print_usage += results["print_usage"]
        except Exception:
            pass

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
        metrics = get_python_metrics(f)
        total_funcs += metrics["functions"]
        typed_funcs += metrics["typed_returns"]

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
    total_metrics = {"functions": 0, "branches": 0}

    for f in files:
        metrics = get_python_metrics(f)
        total_metrics["functions"] += metrics["functions"]
        total_metrics["branches"] += metrics["branches"]

    avg_complexity = calculate_complexity(total_metrics)

    score = 10
    if avg_complexity > 10:
        score -= 5
    elif avg_complexity > 5:
        score -= 2

    details = f"Avg Complexity (branches/func): {avg_complexity:.1f}"

    return {"grade": max(0, score), "details": details}


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
        generate_markdown_report(
            category_id=cat_code,
            category_name=name,
            grade=info["grade"],
            details=info["details"],
            recommendations=["See detailed findings"],
        )

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
    for cat_code, info in scores.items():
        comp_content += f"| {CATEGORIES[cat_code]} | {info['grade']:.1f} | - |\n"

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
            issue_path = generate_issue_document(
                category_id=cat_code,
                category_name=CATEGORIES[cat_code],
                grade=info["grade"],
                details=info["details"],
            )
            comp_content += f"- Created issue: `{issue_path.name}` (Grade: {info['grade']:.1f})\n"

    Path("docs/assessments/Comprehensive_Assessment.md").write_text(comp_content, encoding="utf-8")
    logger.info("Assessment complete.")


if __name__ == "__main__":
    main()
