"""Enforce published AffineDrift limits for the new research admission surface."""

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1] / "src/affine_control/historical_research"


@pytest.mark.parametrize("budget", ["lines", "parameters"])
def test_historical_research_functions_respect_repository_budgets(budget: str) -> None:
    violations: list[str] = []
    for path in sorted(ROOT.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        assert len(source.splitlines()) <= 400, path.name
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            arguments = node.args
            size = node.end_lineno - node.lineno + 1
            count = len(arguments.posonlyargs) + len(arguments.args) + len(arguments.kwonlyargs)
            exceeded = size > 50 if budget == "lines" else count > 4
            if exceeded:
                violations.append(
                    f"{path.name}:{node.lineno} {node.name}: {size} lines/{count} parameters"
                )
    assert not violations, "\n".join(violations)
