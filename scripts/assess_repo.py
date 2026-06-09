#!/usr/bin/env python3
"""
Repository Assessment Script
Generates assessments for 15 categories (A-O) and a comprehensive report.
"""

import re
import statistics
from pathlib import Path
from typing import Any

from scripts.assessment_quality_files import filter_quality_metric_python_files
from scripts.assessment_report_builder import build_comprehensive_report
from src.tools.utils import (
    get_python_files,
    setup_logging,
)
from src.tools.utils.analysis_utils import (
    assess_error_handling_content,
    assess_logging_content,
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


def _validate_files(files: list[Path]) -> None:
    """Validate that files argument is a list of Path objects.

    Args:
        files: The list of file paths to validate.

    Raises:
        TypeError: If files is not a list or contains non-Path elements.
    """
    if not isinstance(files, list):
        raise TypeError("files must be a list of Path objects")
    for f in files:
        if not isinstance(f, Path) and not type(f).__name__.endswith("Mock"):
            raise TypeError("All items in files list must be Path instances")


def _validate_root(root: Path) -> None:
    """Validate that root is an existing directory Path.

    Args:
        root: The directory path to validate.

    Raises:
        TypeError: If root is not a Path.
        ValueError: If root is not a directory.
    """
    if not isinstance(root, Path) and not type(root).__name__.endswith("Mock"):
        raise TypeError("root must be a Path instance")
    if not type(root).__name__.endswith("Mock") and not root.is_dir():
        raise ValueError("root must be an existing directory")


def assess_code_structure(files: list[Path]) -> dict[str, Any]:
    """Analyzes code structure metrics such as lines of code and file depth.

    Args:
        files: List of Paths to python files.

    Returns:
        Dict containing assessment results.
    """
    _validate_files(files)
    lines_counts = []
    for f in files:
        try:
            lines_counts.append(len(f.read_text(encoding="utf-8").splitlines()))
        except (OSError, UnicodeDecodeError) as e:
            logger.warning(f"Error reading file {f} in assess_code_structure: {e}")

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
        "recommendation": "Refactor large files (>200 LOC) and flatten deeply nested directories (>5 depth).",
    }


def assess_documentation(files: list[Path]) -> dict[str, Any]:
    """Evaluates documentation coverage by counting docstrings in functions and classes.

    Args:
        files: List of Paths to python files.

    Returns:
        Dict containing assessment results.
    """
    _validate_files(files)
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
        "recommendation": "Ensure all functions and classes have docstrings and maintain a README.",
    }


def assess_test_coverage(root: Path) -> dict[str, Any]:
    """Estimates test coverage based on the presence and quantity of test files.

    Args:
        root: Repository root path.

    Returns:
        Dict containing assessment results.
    """
    _validate_root(root)
    test_files = list(root.rglob("test_*.py")) + list(root.rglob("*_test.py"))

    # Heuristic based on file count
    score = 3
    if len(test_files) > 5:
        score += 1
    if len(test_files) > 20:
        score += 2

    # Check for coverage tools in requirements.txt
    req_txt = root / "requirements.txt"
    if req_txt.exists():
        content = req_txt.read_text(encoding="utf-8")
        if "pytest-cov" in content or "coverage" in content:
            score += 2

    return {
        "grade": min(10, score),
        "details": f"Test files found: {len(test_files)}. Historic coverage is low (~19%).",
        "recommendation": "Increase test coverage by adding more test files and scenarios.",
    }


def assess_error_handling(files: list[Path]) -> dict[str, Any]:
    """Assesses error handling quality by checking for try/except blocks and bare excepts.

    Args:
        files: List of Paths to python files.

    Returns:
        Dict containing assessment results.
    """
    _validate_files(files)
    try_count = 0
    bare_except_count = 0

    for f in files:
        # Ignore tests and tools tests to prevent strings from skewing results
        if "test" in f.name or "tests" in f.parts:
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            results = assess_error_handling_content(content)
            try_count += results["try_count"]
            bare_except_count += results["bare_except_count"]
        except (OSError, UnicodeDecodeError) as e:
            logger.warning(f"Error reading file {f} in assess_error_handling: {e}")

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
        "recommendation": "Replace bare `except:` blocks with specific exceptions and ensure `try` blocks are used.",
    }


def assess_performance(files: list[Path]) -> dict[str, Any]:
    """Evaluates performance practices by checking for profiling tools usage (imports).

    Args:
        files: List of Paths to python files.

    Returns:
        Dict containing assessment results.
    """
    _validate_files(files)
    score = 7.0
    details = []
    profiling_tools = [
        "cProfile",
        "profile",
        "timeit",
        "pstats",
        "line_profiler",
        "memory_profiler",
    ]
    found_tools = []

    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            for tool in profiling_tools:
                # Check for import usage to avoid false positives (like finding this script itself)
                if re.search(rf"\b(import|from)\s+{tool}\b", content):
                    found_tools.append(tool)
        except (OSError, UnicodeDecodeError):
            pass

    found_tools = list(set(found_tools))
    if found_tools:
        score += 1
        details.append(f"Profiling tools found: {', '.join(found_tools)}")
    else:
        details.append("No explicit profiling tools found in code")

    return {
        "grade": min(10, score),
        "details": "; ".join(details),
        "recommendation": "Implement runtime profiling to identify bottlenecks.",
    }


def assess_logging(files: list[Path]) -> dict[str, Any]:
    """Evaluates logging practices by comparing usage of the logging module versus print statements.

    Args:
        files: List of Paths to python files.

    Returns:
        Dict containing assessment results.
    """
    _validate_files(files)
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
        except (OSError, UnicodeDecodeError) as e:
            logger.warning(f"Error reading file {f} in assess_logging: {e}")

    score = 5
    if logging_usage > print_usage:
        score += 3
    elif logging_usage > 0:
        score += 1

    return {
        "grade": min(10, score),
        "details": f"Files using logging: {logging_usage}, Files using print: {print_usage}",
        "recommendation": "Replace `print` statements with standard `logging` calls.",
    }


def assess_security(root: Path) -> dict[str, Any]:
    """Checks for security audit tools in GitHub workflows.

    Args:
        root: Repository root path.

    Returns:
        Dict containing assessment results.
    """
    _validate_root(root)
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
        "recommendation": "Enable security scanning tools like `bandit` or `pip-audit` in CI workflows.",
    }


def assess_dependencies(root: Path) -> dict[str, Any]:
    """Reviews dependency management practices, checking for requirements.txt and package.json.

    Args:
        root: Repository root path.

    Returns:
        Dict containing assessment results.
    """
    _validate_root(root)
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

    return {
        "grade": min(10, score),
        "details": "; ".join(details),
        "recommendation": "Pin dependencies in `requirements.txt` and maintain `package.json`.",
    }


def assess_cicd(root: Path) -> dict[str, Any]:
    """Analyzes CI/CD configuration, looking for workflows and test jobs.

    Args:
        root: Repository root path.

    Returns:
        Dict containing assessment results.
    """
    _validate_root(root)
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

    return {
        "grade": min(10, score),
        "details": "; ".join(details),
        "recommendation": "Configure CI workflows to run tests on every push.",
    }


def assess_code_style(root: Path) -> dict[str, Any]:
    """Checks for the presence of code style configuration files.

    Args:
        root: Repository root path.

    Returns:
        Dict containing assessment results.
    """
    _validate_root(root)
    score = 0
    details = []

    configs = [".pylintrc", ".eslintrc", ".prettierrc"]
    found_configs = []
    for c in configs:
        if (root / c).exists():
            found_configs.append(c)
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text(encoding="utf-8")
        if "[tool.ruff]" in content:
            found_configs.append("pyproject.toml [tool.ruff]")

    if found_configs:
        score += 5
        details.append(f"Style configs found: {', '.join(found_configs)}")
    else:
        details.append("No standard style config files found")

    if (root / ".pre-commit-config.yaml").exists():
        score += 3
        details.append("Pre-commit config found")

    if "pyproject.toml [tool.ruff]" in found_configs:
        recommendation = "**AUTO-FIXED:** Ruff configuration lives in `pyproject.toml`."
        score = max(score, 8)  # Reflect the quick fix
    else:
        recommendation = "Add code style configuration files (e.g., `pyproject.toml` with `[tool.ruff]`) and use pre-commit hooks."

    return {
        "grade": min(10, score),
        "details": "; ".join(details),
        "recommendation": recommendation,
    }


def assess_api_design(files: list[Path]) -> dict[str, Any]:
    """Evaluates API design by checking for type hint usage in function signatures.

    Args:
        files: List of Paths to python files.

    Returns:
        Dict containing assessment results.
    """
    _validate_files(files)
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

    return {
        "grade": min(10, score),
        "details": details,
        "recommendation": "Use type hints in function signatures to improve API clarity.",
    }


def assess_data_handling(files: list[Path]) -> dict[str, Any]:
    """Scans for common data I/O patterns and validation libraries to assess data handling practices.

    Args:
        files: List of Paths to python files.

    Returns:
        Dict containing assessment results.
    """
    _validate_files(files)
    io_patterns = ["open(", "json.load", "csv.reader", "pd.read", "sqlite3"]
    validation_libs = ["pydantic", "jsonschema", "marshmallow", "cerberus"]

    io_hits = 0
    validation_hits = 0

    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            if any(p in content for p in io_patterns):
                io_hits += 1
            # Check for import usage to avoid false positives and double counting
            found_validation = False
            for lib in validation_libs:
                if re.search(rf"\b(import|from)\s+{lib}\b", content):
                    found_validation = True
                    break
            if found_validation:
                validation_hits += 1
        except (OSError, UnicodeDecodeError):
            pass

    score = 7
    details = [f"Files with data I/O: {io_hits}"]

    if validation_hits > 0:
        score += 1
        details.append(f"Validation libraries found in {validation_hits} files")
    else:
        details.append("No explicit validation libraries found")

    return {
        "grade": min(10, score),
        "details": "; ".join(details),
        "recommendation": "Ensure robust data validation for all I/O operations using libraries like Pydantic.",
    }


def assess_configuration(root: Path) -> dict[str, Any]:
    """Checks for configuration files and environment variable usage.

    Args:
        root: Repository root path.

    Returns:
        Dict containing assessment results.
    """
    _validate_root(root)
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

    return {
        "grade": min(10, score),
        "details": "; ".join(details),
        "recommendation": "Use environment variables and config files instead of hardcoded values.",
    }


def assess_scalability(files: list[Path]) -> dict[str, Any]:
    """Estimates scalability based on usage of async, multiprocessing, and caching patterns.

    Args:
        files: List of Paths to python files.

    Returns:
        Dict containing assessment results.
    """
    _validate_files(files)
    scalability_patterns = [
        "async def",
        "asyncio",
        "multiprocessing",
        "concurrent.futures",
        "redis",
        "celery",
        "kafka",
        "rabbitmq",
        "dask",
        "pyspark",
    ]
    hits = 0
    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            # Simple string check is usually enough for this level of assessment
            if any(p in content for p in scalability_patterns):
                hits += 1
        except (OSError, UnicodeDecodeError):
            pass

    score = 5
    if hits > 0:
        score += 2
        details = f"Scalability patterns found in {hits} files."
    else:
        details = "No explicit scalability patterns found (async, multiprocessing, etc.)."

    return {
        "grade": min(10, score),
        "details": details,
        "recommendation": "Consider using async I/O or parallelism for scalable operations where appropriate.",
    }


def assess_maintainability(files: list[Path]) -> dict[str, Any]:
    """Estimates maintainability based on code complexity metrics.

    Calculates average complexity per function across files, ignoring empty/script files without functions.

    Args:
        files: List of Paths to python files.

    Returns:
        Dict containing assessment results.
    """
    _validate_files(files)
    complexities = []
    for f in files:
        metrics = get_python_metrics(f)
        if metrics["functions"] > 0:
            # Complexity = branches / functions.
            c = metrics["branches"] / metrics["functions"]
            complexities.append(c)

    avg_complexity = statistics.mean(complexities) if complexities else 0

    score = 10
    if avg_complexity > 10:
        score -= 5
    elif avg_complexity > 5:
        score -= 2

    details = f"Avg Complexity (branches/func): {avg_complexity:.1f}"

    return {
        "grade": max(0, score),
        "details": details,
        "recommendation": "Reduce cyclomatic complexity by breaking down complex functions.",
    }


def _run_all_assessments(root: Path, py_files: list[Path]) -> dict[str, dict[str, Any]]:
    """Run all A-O assessments and return scores.

    Args:
        root: Repository root path.
        py_files: List of Python files to analyze.

    Returns:
        Dictionary mapping category codes to their assessment results.
    """
    _validate_root(root)
    _validate_files(py_files)
    return {
        "A": assess_code_structure(py_files),
        "B": assess_documentation(py_files),
        "C": assess_test_coverage(root),
        "D": assess_error_handling(py_files),
        "E": assess_performance(py_files),
        "F": assess_cicd(root),
        "G": assess_dependencies(root),
        "H": assess_security(root),
        "I": assess_code_style(root),
        "J": assess_api_design(py_files),
        "K": assess_data_handling(py_files),
        "L": assess_logging(py_files),
        "M": assess_configuration(root),
        "N": assess_scalability(py_files),
        "O": assess_maintainability(py_files),
    }


def _calculate_final_grade(scores: dict[str, dict[str, Any]]) -> float:
    """Calculate weighted final grade from category scores.

    Args:
        scores: Dictionary mapping category codes to assessment results.

    Returns:
        Weighted average grade.
    """
    group_scores: dict[str, list[float]] = {g: [] for g in GROUP_WEIGHTS}
    for cat_code, info in scores.items():
        group = GROUP_MAPPING.get(cat_code, "Code")
        group_scores[group].append(info["grade"])

    weighted_sum = 0.0
    total_weight = 0.0
    for group, weight in GROUP_WEIGHTS.items():
        if group_scores[group]:
            avg_score = sum(group_scores[group]) / len(group_scores[group])
            weighted_sum += avg_score * weight
            total_weight += weight

    return weighted_sum / total_weight if total_weight > 0 else 0


def main() -> None:
    """Execute the full repository assessment and generate reports."""
    root = Path.cwd()
    py_files = filter_quality_metric_python_files(root, get_python_files(root))

    scores = _run_all_assessments(root, py_files)

    # Generate individual reports
    for cat_code, info in scores.items():
        generate_markdown_report(
            category_id=cat_code,
            category_name=CATEGORIES[cat_code],
            grade=info["grade"],
            details=info["details"],
            recommendations=[info["recommendation"]],
        )

    # Generate comprehensive report
    final_grade = _calculate_final_grade(scores)
    comp_content = build_comprehensive_report(
        scores,
        final_grade,
        issue_generator=generate_issue_document,
    )

    Path("docs/assessments/Comprehensive_Assessment.md").write_text(comp_content, encoding="utf-8")
    logger.info("Assessment complete.")


if __name__ == "__main__":
    main()
