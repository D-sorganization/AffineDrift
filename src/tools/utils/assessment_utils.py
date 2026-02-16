"""Shared definitions and utilities for repository assessments.

This module contains the standard assessment categories, group weights,
and mappings used by various assessment and reporting scripts.
"""

from __future__ import annotations

from src.core.contracts import require

# Assessment definitions (Standardized A-O)
ASSESSMENT_DEFINITIONS = {
    "A": {"name": "Architecture", "description": "Code structure and organization"},
    "B": {"name": "Hygiene & Quality", "description": "Linting, formatting, code quality"},
    "C": {"name": "Documentation", "description": "README, docstrings, comments"},
    "D": {"name": "User Experience", "description": "CLI, API usability"},
    "E": {"name": "Performance", "description": "Efficiency, optimization"},
    "F": {"name": "Installation", "description": "Setup, dependencies, packaging"},
    "G": {"name": "Testing", "description": "Test coverage, test quality"},
    "H": {"name": "Error Handling", "description": "Exception handling, logging"},
    "I": {"name": "Security", "description": "Vulnerabilities, best practices"},
    "J": {"name": "API Design", "description": "Interface consistency"},
    "K": {"name": "Data Handling", "description": "Data validation, serialization"},
    "L": {"name": "Logging", "description": "Logging practices"},
    "M": {"name": "Configuration", "description": "Config management"},
    "N": {"name": "Scalability", "description": "Performance at scale"},
    "O": {"name": "Maintainability", "description": "Code maintainability"},
}

# Mapping of A-O categories to descriptive names (used in legacy scripts)
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

# Grouping weights for comprehensive reports
GROUP_WEIGHTS = {
    "Code": 0.25,
    "Testing": 0.15,
    "Docs": 0.10,
    "Security": 0.15,
    "Perf": 0.15,
    "Ops": 0.10,
    "Design": 0.10,
}

# Mapping of categories to groups
GROUP_MAPPING = {
    "A": "Code",
    "D": "Code",
    "I": "Code",
    "O": "Code",
    "K": "Code",
    "L": "Code",
    "C": "Testing",
    "G": "Ops",
    "B": "Docs",
    "F": "Security",
    "E": "Perf",
    "H": "Ops",
    "M": "Ops",
    "J": "Design",
    "N": "Design",
}


# Pragmatic Programmer principles and their assessment criteria
PRAGMATIC_PRINCIPLES = {
    "DRY": {
        "name": "Don't Repeat Yourself",
        "description": "Every piece of knowledge must have a single, unambiguous representation",
        "weight": 2.0,
    },
    "ORTHOGONALITY": {
        "name": "Orthogonality & Decoupling",
        "description": "Eliminate effects between unrelated things",
        "weight": 1.5,
    },
    "REVERSIBILITY": {
        "name": "Reversibility & Flexibility",
        "description": "Make decisions reversible; avoid painting yourself into a corner",
        "weight": 1.0,
    },
    "QUALITY": {
        "name": "Code Quality & Craftsmanship",
        "description": "Good enough software; know when to stop",
        "weight": 1.5,
    },
    "ROBUSTNESS": {
        "name": "Error Handling & Robustness",
        "description": "Crash early; use assertions; handle errors gracefully",
        "weight": 2.0,
    },
    "TESTING": {
        "name": "Testing & Validation",
        "description": "Test early, test often, test automatically",
        "weight": 2.0,
    },
    "DOCUMENTATION": {
        "name": "Documentation & Communication",
        "description": "It's all writing; document the why, not just the what",
        "weight": 1.0,
    },
    "AUTOMATION": {
        "name": "Automation & Tooling",
        "description": "Don't use manual procedures; automate everything",
        "weight": 1.5,
    },
}


def classify_assessment_category(source_name: str, description: str = "") -> str:
    """Classify an assessment finding into a standard category name.

    Args:
        source_name: Name of the source report or category ID.
        description: Optional detailed description for keyword matching.

    Returns:
        A standardized category name matching CATEGORIES values.
    """
    require(len(source_name) > 0, "source_name must not be empty")
    text = (source_name + " " + description).lower()

    # Mappings aligned with CATEGORIES (A-O)
    mappings = {
        "Code Structure": ["code structure", "architecture", "structure", "Assessment_A"],
        "Documentation": ["documentation", "readme", "docstring", "Assessment_B"],
        "Test Coverage": ["test coverage", "testing", "coverage", "Assessment_C"],
        "Error Handling": ["error handling", "exception", "try/except", "Assessment_D"],
        "Performance": ["performance", "profiling", "optimization", "Assessment_E"],
        "Security": ["security", "vulnerability", "audit", "Assessment_F"],
        "Dependencies": ["dependencies", "requirements", "package", "Assessment_G"],
        "CI/CD": ["ci/cd", "ci", "cd", "workflow", "pipeline", "Assessment_H"],
        "Code Style": ["code style", "linting", "formatting", "Assessment_I"],
        "API Design": ["api design", "api", "interface", "Assessment_J"],
        "Data Handling": ["data handling", "validation", "serialization", "Assessment_K"],
        "Logging": ["logging", "log", "Assessment_L"],
        "Configuration": ["configuration", "config", "env var", "Assessment_M"],
        "Scalability": ["scalability", "complexity", "Assessment_N"],
        "Maintainability": ["maintainability", "Assessment_O"],
    }

    for category, keywords in mappings.items():
        if any(k in text for k in keywords) or any(k in source_name for k in keywords):
            return category

    return "General"
