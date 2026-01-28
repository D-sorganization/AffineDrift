"""Tests for the repository assessment script.

These tests verify the assess_repo module's ability to analyze code structure,
find Python files, and generate assessment reports.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add scripts directory to path
scripts_dir = str(Path(__file__).parents[1] / "scripts")
if scripts_dir not in sys.path:
    sys.path.append(scripts_dir)

import assess_repo  # noqa: E402


def test_get_python_files():
    """Test finding python files."""
    files = assess_repo.get_python_files(Path.cwd())
    assert len(files) > 0
    # Ensure this test file is found
    assert any("test_assess_repo.py" in str(f) for f in files)


def test_assess_code_structure_basic():
    """Test code structure assessment logic."""
    mock_file = MagicMock()
    mock_file.read_text.return_value = "print('hello')\n" * 10
    mock_file.relative_to.return_value.parts = ["a", "b"]

    result = assess_repo.assess_code_structure([mock_file])
    assert result["grade"] == 10
    assert "Avg LOC" in result["details"]


def test_assess_code_structure_penalties():
    """Test code structure assessment with penalties."""
    mock_file = MagicMock()
    # > 200 lines
    mock_file.read_text.return_value = "print('hello')\n" * 201
    # Depth > 5
    mock_file.relative_to.return_value.parts = ["a", "b", "c", "d", "e", "f"]

    result = assess_repo.assess_code_structure([mock_file])
    # 10 - 2 (LOC) - 2 (Depth) = 6
    assert result["grade"] == 6


def test_assess_documentation_mock():
    """Test documentation assessment with mocked content."""
    mock_file = MagicMock()
    mock_file.read_text.return_value = '''
def my_func():
    """This is a docstring."""
    return True

class MyClass:
    """Class docstring."""
    pass
'''
    with patch("pathlib.Path.rglob") as mock_rglob:
        mock_rglob.return_value = []  # No READMEs
        result = assess_repo.assess_documentation([mock_file])
        assert result["grade"] == 10
        assert "100.0%" in result["details"]


def test_assess_documentation_partial():
    """Test documentation assessment with partial coverage."""
    mock_file = MagicMock()
    mock_file.read_text.return_value = '''
def my_func():
    return True

def my_func2():
    """Docstring"""
    return None  # noqa: placeholder for test fixture
'''
    with patch("pathlib.Path.rglob") as mock_rglob:
        mock_rglob.return_value = []  # No READMEs
        result = assess_repo.assess_documentation([mock_file])
        # 50% coverage => grade 5
        assert result["grade"] == 5


def test_assess_test_coverage():
    """Test test coverage assessment."""
    with patch("pathlib.Path.rglob") as mock_rglob:
        mock_rglob.return_value = [Path("test_a.py"), Path("test_b.py")]
        result = assess_repo.assess_test_coverage(Path("/tmp"))
        # 2 files <= 5 => score 3
        assert result["grade"] == 3


def test_assess_test_coverage_high():
    """Test test coverage assessment with many tests."""
    with patch("pathlib.Path.rglob") as mock_rglob:
        # > 20 files
        mock_rglob.return_value = [Path(f"test_{i}.py") for i in range(25)]
        result = assess_repo.assess_test_coverage(Path("/tmp"))
        # 3 + 1 (>5) + 2 (>20) = 6. Limited to 10.
        assert result["grade"] == 6


def test_assess_error_handling_mock():
    """Test error handling assessment."""
    mock_file = MagicMock()
    mock_file.read_text.return_value = """
try:
    pass
except Exception:
    pass
"""
    result = assess_repo.assess_error_handling([mock_file])
    assert result["grade"] == 7


def test_assess_error_handling_bare_except():
    """Test error handling assessment with bare excepts."""
    mock_file = MagicMock()
    mock_file.read_text.return_value = (
        """
try:
    pass
except:
    pass
"""
        * 6
    )
    result = assess_repo.assess_error_handling([mock_file])
    # 6 bare excepts (>5) => -2
    # try_count = 6 (<=20) => no bonus
    # Base 7 - 2 = 5
    assert result["grade"] == 5


def test_assess_logging():
    """Test logging assessment."""
    mock_file = MagicMock()
    mock_file.name = "app.py"
    mock_file.read_text.return_value = "logging.info('test')"

    result = assess_repo.assess_logging([mock_file])
    # Base 5. logging > print (1 > 0) => +3. Total 8.
    assert result["grade"] == 8


def test_assess_logging_print_usage():
    """Test logging assessment with print usage."""
    mock_file = MagicMock()
    mock_file.name = "app.py"
    mock_file.read_text.return_value = "print('test')"

    result = assess_repo.assess_logging([mock_file])
    # Base 5. logging (0) not > print (1). logging == 0 => no +1.
    assert result["grade"] == 5


def test_assess_security():
    """Test security assessment."""
    with patch("pathlib.Path.glob") as mock_glob:
        mock_workflow = MagicMock()
        mock_workflow.read_text.return_value = "uses: pypa/gh-action-pip-audit"
        mock_glob.return_value = [mock_workflow]

        result = assess_repo.assess_security(Path("/tmp"))
        # Base 7 + 2 = 9
        assert result["grade"] == 9


def test_assess_dependencies():
    """Test dependency assessment."""
    root = MagicMock()
    req_txt = root / "requirements.txt"
    req_txt.exists.return_value = True
    req_txt.read_text.return_value = "flask==2.0.0\nrequests==2.0.0"

    pkg_json = root / "package.json"
    pkg_json.exists.return_value = True

    result = assess_repo.assess_dependencies(root)
    # req found (+5), pinned > 0.5 (+3), pkg.json found (+2) => 10
    assert result["grade"] == 10


def test_assess_cicd():
    """Test CI/CD assessment."""
    root = MagicMock()
    workflow_dir = root / ".github" / "workflows"
    workflow_dir.exists.return_value = True

    mock_workflow = MagicMock()
    mock_workflow.read_text.return_value = "run: pytest"
    workflow_dir.glob.return_value = [mock_workflow]

    result = assess_repo.assess_cicd(root)
    # Workflows found (+5), run tests (+3) => 8
    assert result["grade"] == 8


def test_assess_code_style():
    """Test code style assessment."""
    root = MagicMock()
    (root / "ruff.toml").exists.return_value = True
    (root / ".pre-commit-config.yaml").exists.return_value = True

    result = assess_repo.assess_code_style(root)
    # Config found (+5), pre-commit found (+3) => 8
    assert result["grade"] == 8


def test_assess_api_design():
    """Test API design assessment."""
    mock_file = MagicMock()
    # One function with return type hint
    mock_file.read_text.return_value = "def foo() -> int: pass"

    result = assess_repo.assess_api_design([mock_file])
    # Base 5. 1/1 typed => +5. Total 10.
    assert result["grade"] == 10


def test_assess_data_handling():
    """Test data handling assessment."""
    mock_file = MagicMock()
    mock_file.read_text.return_value = "json.load(f)"

    result = assess_repo.assess_data_handling([mock_file])
    assert result["grade"] == 7
    assert "Files with data I/O: 1" in result["details"]


def test_assess_configuration():
    """Test configuration assessment."""
    root = MagicMock()
    (root / ".env.example").exists.return_value = True

    mock_file = MagicMock()
    mock_file.read_text.return_value = "os.environ['KEY']"
    root.rglob.return_value = [mock_file]

    result = assess_repo.assess_configuration(root)
    # Config found (+5), env used (+3) => 8
    assert result["grade"] == 8


def test_assess_scalability_maintainability():
    """Test scalability assessment."""
    mock_file = MagicMock()
    # High complexity: many branches
    mock_file.read_text.return_value = "if a: pass\n" * 20 + "def foo(): pass"

    result = assess_repo.assess_scalability_maintainability([mock_file])
    # Complexity > 10 => -5. 10 - 5 = 5.
    assert result["grade"] == 5


@patch("assess_repo.generate_markdown_report")
@patch("assess_repo.generate_issue_document")
@patch("pathlib.Path.write_text")
@patch("assess_repo.get_python_files")
def test_main(mock_get_files, mock_write, mock_issue, mock_report):
    """Test main execution."""
    mock_get_files.return_value = []

    assess_repo.main()

    assert mock_report.call_count == 15
    assert mock_write.called
