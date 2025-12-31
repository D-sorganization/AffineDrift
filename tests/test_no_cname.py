import os
import pytest

def test_no_cname_in_root():
    """Ensure no CNAME file exists in the repository root."""
    assert not os.path.exists("CNAME"), "CNAME file found in root! It should not be present to avoid GitHub Pages redirect issues."

def test_no_cname_in_docs():
    """Ensure no CNAME file exists in the docs directory."""
    assert not os.path.exists("docs/CNAME"), "CNAME file found in docs/! It should not be present to avoid GitHub Pages redirect issues."
