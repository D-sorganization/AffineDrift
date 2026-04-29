from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MypyError:
    """Parsed mypy error."""

    file: str
    line: int
    column: int
    severity: str  # "error" or "note"
    message: str
    code: str  # e.g., "union-attr", "valid-type", "import-untyped"


@dataclass
class Fix:
    """A fix to apply."""

    file: str
    line: int
    description: str
    strategy: str  # "real-fix" or "suppression"
    original_code: str = ""


@dataclass
class AgentReport:
    """Report of all actions taken."""

    total_errors: int = 0
    errors_fixed: int = 0
    real_fixes: int = 0
    suppressions: int = 0
    files_modified: list[str] = field(default_factory=list)
    fixes_applied: list[str] = field(default_factory=list)
    skipped_reasons: list[str] = field(default_factory=list)
