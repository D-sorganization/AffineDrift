import sys
from pathlib import Path
import pytest

# Add scripts dir to path so we can import assess_repo
scripts_dir = Path(__file__).parents[1] / "scripts"
sys.path.append(str(scripts_dir))

import assess_repo

def test_get_python_files(tmp_path):
    (tmp_path / "test.py").touch()
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "ignored.py").touch()

    files = assess_repo.get_python_files(tmp_path)
    assert len(files) == 1
    assert files[0].name == "test.py"

def test_assess_documentation(tmp_path):
    f = tmp_path / "test_doc.py"
    f.write_text('def foo():\n    """Docstring."""\n    pass\n')

    result = assess_repo.assess_documentation([f])
    assert result["grade"] > 0
    assert "Docstring Coverage: 100.0%" in result["details"]

def test_assess_error_handling(tmp_path):
    f = tmp_path / "test_err.py"
    f.write_text('try:\n    pass\nexcept Exception:\n    pass\n')

    result = assess_repo.assess_error_handling([f])
    assert result["grade"] >= 0
    # It counts bare excepts (except:) not caught excepts (except Exception:)

def test_assess_test_coverage_files_count(tmp_path):
    # Setup dummy test files
    (tmp_path / "test_1.py").touch()
    (tmp_path / "test_2.py").touch()
    (tmp_path / "test_3.py").touch()
    (tmp_path / "test_4.py").touch()
    (tmp_path / "test_5.py").touch()
    (tmp_path / "test_6.py").touch()

    result = assess_repo.assess_test_coverage(tmp_path)
    # > 5 test files should give score > 3
    assert result["grade"] > 3
