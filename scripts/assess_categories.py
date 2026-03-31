"""Individual category assessment functions for the Repository Assessment script.

Each function analyses one aspect of the repository and returns a dict with:
  - "grade"          : float score 0–10
  - "details"        : one-line summary string
  - "recommendation" : actionable improvement suggestion

Functions are grouped by the 15 assessment categories A through O.
"""

from __future__ import annotations

import re
import statistics
from pathlib import Path
from typing import Any

from src.tools.utils import setup_logging
from src.tools.utils.analysis_utils import (
    assess_error_handling_content,
    assess_logging_content,
    get_python_metrics,
)

logger = setup_logging(__name__, format_string="%(message)s")


# ---------------------------------------------------------------------------
# A – Code structure
# ---------------------------------------------------------------------------


def assess_code_structure(files: list[Path]) -> dict[str, Any]:
    """Analyse code structure: lines of code per file and directory depth.

    Args:
        files: Python source files to examine.

    Returns:
        Assessment dict with grade, details, and recommendation.
    """
    lines_counts: list[int] = []
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
        "details": (
            f"Files: {len(files)}, Avg LOC: {avg_loc:.1f}, "
            f"Max LOC: {max_loc}, Max Depth: {max_depth}"
        ),
        "recommendation": (
            "Refactor large files (>200 LOC) and flatten deeply nested directories (>5 depth)."
        ),
    }


# ---------------------------------------------------------------------------
# B – Documentation
# ---------------------------------------------------------------------------


def assess_documentation(files: list[Path]) -> dict[str, Any]:
    """Evaluate docstring coverage across functions and classes.

    Args:
        files: Python source files to examine.

    Returns:
        Assessment dict with grade, details, and recommendation.
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
        "details": (
            f"Docstring Coverage: {coverage:.1f}% ({docstring_count}/{total_defs}), "
            f"READMEs found: {len(readmes)}"
        ),
        "recommendation": "Ensure all functions and classes have docstrings and maintain a README.",
    }


# ---------------------------------------------------------------------------
# C – Test coverage
# ---------------------------------------------------------------------------


def assess_test_coverage(root: Path) -> dict[str, Any]:
    """Estimate test coverage from the number of test files present.

    Args:
        root: Repository root directory.

    Returns:
        Assessment dict with grade, details, and recommendation.
    """
    test_files = list(root.rglob("test_*.py")) + list(root.rglob("*_test.py"))

    score = 3
    if len(test_files) > 5:
        score += 1
    if len(test_files) > 20:
        score += 2

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


# ---------------------------------------------------------------------------
# D – Error handling
# ---------------------------------------------------------------------------


def assess_error_handling(files: list[Path]) -> dict[str, Any]:
    """Assess try/except usage and presence of bare ``except:`` clauses.

    Args:
        files: Python source files to examine.

    Returns:
        Assessment dict with grade, details, and recommendation.
    """
    try_count = 0
    bare_except_count = 0

    for f in files:
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
        "recommendation": (
            "Replace bare `except:` blocks with specific exceptions and "
            "ensure `try` blocks are used."
        ),
    }


# ---------------------------------------------------------------------------
# E – Performance
# ---------------------------------------------------------------------------


def assess_performance(files: list[Path]) -> dict[str, Any]:
    """Check for profiling tool imports as a proxy for performance awareness.

    Args:
        files: Python source files to examine.

    Returns:
        Assessment dict with grade, details, and recommendation.
    """
    score = 7.0
    profiling_tools = [
        "cProfile",
        "profile",
        "timeit",
        "pstats",
        "line_profiler",
        "memory_profiler",
    ]
    found_tools: list[str] = []

    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            for tool in profiling_tools:
                if re.search(rf"\b(import|from)\s+{tool}\b", content):
                    found_tools.append(tool)
        except (OSError, UnicodeDecodeError):
            pass

    found_tools = list(set(found_tools))
    if found_tools:
        score += 1
        details = f"Profiling tools found: {', '.join(found_tools)}"
    else:
        details = "No explicit profiling tools found in code"

    return {
        "grade": min(10, score),
        "details": details,
        "recommendation": "Implement runtime profiling to identify bottlenecks.",
    }


# ---------------------------------------------------------------------------
# F – Security
# ---------------------------------------------------------------------------


def assess_security(root: Path) -> dict[str, Any]:
    """Check CI workflows for security scanning tools (bandit, pip-audit).

    Args:
        root: Repository root directory.

    Returns:
        Assessment dict with grade, details, and recommendation.
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
        "recommendation": (
            "Enable security scanning tools like `bandit` or `pip-audit` in CI workflows."
        ),
    }


# ---------------------------------------------------------------------------
# G – Dependencies
# ---------------------------------------------------------------------------


def assess_dependencies(root: Path) -> dict[str, Any]:
    """Review dependency management: requirements.txt pinning and package.json.

    Args:
        root: Repository root directory.

    Returns:
        Assessment dict with grade, details, and recommendation.
    """
    score = 0
    details: list[str] = []

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
        "recommendation": ("Pin dependencies in `requirements.txt` and maintain `package.json`."),
    }


# ---------------------------------------------------------------------------
# H – CI/CD
# ---------------------------------------------------------------------------


def assess_cicd(root: Path) -> dict[str, Any]:
    """Analyse CI/CD configuration: workflow count and test job presence.

    Args:
        root: Repository root directory.

    Returns:
        Assessment dict with grade, details, and recommendation.
    """
    score = 0
    details: list[str] = []
    workflows_dir = root / ".github" / "workflows"
    if workflows_dir.exists():
        workflows = list(workflows_dir.glob("*.yml"))
        if workflows:
            score += 5
            details.append(f"Found {len(workflows)} workflows")
            test_jobs = sum(
                1
                for w in workflows
                if "run: pytest" in w.read_text(encoding="utf-8")
                or "npm test" in w.read_text(encoding="utf-8")
            )
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


# ---------------------------------------------------------------------------
# I – Code style
# ---------------------------------------------------------------------------


def assess_code_style(root: Path) -> dict[str, Any]:
    """Check for style configuration files and pre-commit hooks.

    Args:
        root: Repository root directory.

    Returns:
        Assessment dict with grade, details, and recommendation.
    """
    score = 0
    details: list[str] = []

    configs = [".flake8", "ruff.toml", ".pylintrc", ".eslintrc", ".prettierrc"]
    found_configs = [c for c in configs if (root / c).exists()]

    if found_configs:
        score += 5
        details.append(f"Style configs found: {', '.join(found_configs)}")
    else:
        details.append("No standard style config files found")

    if (root / ".pre-commit-config.yaml").exists():
        score += 3
        details.append("Pre-commit config found")

    return {
        "grade": min(10, score),
        "details": "; ".join(details),
        "recommendation": (
            "Add code style configuration files (e.g., `.flake8`, `ruff.toml`) "
            "and use pre-commit hooks."
        ),
    }


# ---------------------------------------------------------------------------
# J – API design
# ---------------------------------------------------------------------------


def assess_api_design(files: list[Path]) -> dict[str, Any]:
    """Evaluate type-hint adoption in function return signatures.

    Args:
        files: Python source files to examine.

    Returns:
        Assessment dict with grade, details, and recommendation.
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

    return {
        "grade": min(10, score),
        "details": details,
        "recommendation": "Use type hints in function signatures to improve API clarity.",
    }


# ---------------------------------------------------------------------------
# K – Data handling
# ---------------------------------------------------------------------------


def assess_data_handling(files: list[Path]) -> dict[str, Any]:
    """Scan for data I/O patterns and validation library usage.

    Args:
        files: Python source files to examine.

    Returns:
        Assessment dict with grade, details, and recommendation.
    """
    io_patterns = ["open(", "json.load", "csv.reader", "pd.read", "sqlite3"]
    validation_libs = ["pydantic", "jsonschema", "marshmallow", "cerberus"]

    io_hits = 0
    validation_hits = 0

    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            if any(p in content for p in io_patterns):
                io_hits += 1
            if any(re.search(rf"\b(import|from)\s+{lib}\b", content) for lib in validation_libs):
                validation_hits += 1
        except (OSError, UnicodeDecodeError):
            pass

    score = 7
    details_parts = [f"Files with data I/O: {io_hits}"]

    if validation_hits > 0:
        score += 1
        details_parts.append(f"Validation libraries found in {validation_hits} files")
    else:
        details_parts.append("No explicit validation libraries found")

    return {
        "grade": min(10, score),
        "details": "; ".join(details_parts),
        "recommendation": (
            "Ensure robust data validation for all I/O operations using libraries like Pydantic."
        ),
    }


# ---------------------------------------------------------------------------
# L – Logging
# ---------------------------------------------------------------------------


def assess_logging(files: list[Path]) -> dict[str, Any]:
    """Compare logging module usage vs print statement usage.

    Args:
        files: Python source files to examine (test files are skipped).

    Returns:
        Assessment dict with grade, details, and recommendation.
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
        except (OSError, UnicodeDecodeError) as e:
            logger.warning(f"Error reading file {f} in assess_logging: {e}")

    score = 5
    if logging_usage > print_usage:
        score += 3
    elif logging_usage > 0:
        score += 1

    return {
        "grade": min(10, score),
        "details": (f"Files using logging: {logging_usage}, Files using print: {print_usage}"),
        "recommendation": "Replace `print` statements with standard `logging` calls.",
    }


# ---------------------------------------------------------------------------
# M – Configuration
# ---------------------------------------------------------------------------


def assess_configuration(root: Path) -> dict[str, Any]:
    """Check for configuration files and environment variable usage.

    Args:
        root: Repository root directory.

    Returns:
        Assessment dict with grade, details, and recommendation.
    """
    score = 0
    details: list[str] = []

    config_files = [".env.example", "config.py", "settings.py", "pyproject.toml"]
    found = [c for c in config_files if (root / c).exists()]

    if found:
        score += 5
        details.append(f"Config files: {', '.join(found)}")

    environ_usage = sum(
        1
        for f in root.rglob("*.py")
        if "os.environ" in f.read_text(encoding="utf-8", errors="ignore")
    )

    if environ_usage > 0:
        score += 3
        details.append(f"Env vars used in {environ_usage} files")

    return {
        "grade": min(10, score),
        "details": "; ".join(details),
        "recommendation": (
            "Use environment variables and config files instead of hardcoded values."
        ),
    }


# ---------------------------------------------------------------------------
# N – Scalability
# ---------------------------------------------------------------------------


def assess_scalability(files: list[Path]) -> dict[str, Any]:
    """Estimate scalability from async/parallel/caching pattern usage.

    Args:
        files: Python source files to examine.

    Returns:
        Assessment dict with grade, details, and recommendation.
    """
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
        "recommendation": (
            "Consider using async I/O or parallelism for scalable operations where appropriate."
        ),
    }


# ---------------------------------------------------------------------------
# O – Maintainability
# ---------------------------------------------------------------------------


def assess_maintainability(files: list[Path]) -> dict[str, Any]:
    """Estimate maintainability from average cyclomatic complexity.

    Complexity is approximated as (branch count / function count) per file.

    Args:
        files: Python source files to examine.

    Returns:
        Assessment dict with grade, details, and recommendation.
    """
    complexities: list[float] = []
    for f in files:
        metrics = get_python_metrics(f)
        if metrics["functions"] > 0:
            complexities.append(metrics["branches"] / metrics["functions"])

    avg_complexity = statistics.mean(complexities) if complexities else 0

    score = 10
    if avg_complexity > 10:
        score -= 5
    elif avg_complexity > 5:
        score -= 2

    return {
        "grade": max(0, score),
        "details": f"Avg Complexity (branches/func): {avg_complexity:.1f}",
        "recommendation": "Reduce cyclomatic complexity by breaking down complex functions.",
    }
