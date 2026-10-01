"""Reader run environment contracts: Binder, devcontainer, and source downloads (#4538).

Before this issue, a reader could not run the textbook's notebooks anywhere
other than their own machine: no Binder environment, no devcontainer, and
`code-tools: false` hid the source-download menu on every page, including the
pages that show Python reference implementations. Each check below pins one
piece of that run environment to a single file so it cannot silently regress.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
BOOK_FILES = (
    "books/tangent-space-methods.qmd",
    "books/control-is-motion.qmd",
    "books/biomechanics-biology-to-systems.qmd",
    "books/human-motor-control.qmd",
)
BINDER_INCLUDE = "_includes/notebook-binder-launch.qmd"


def _read(relative: str) -> str:
    return (REPO_ROOT / relative).read_text(encoding="utf-8")


def test_environment_yml_installs_from_requirements_txt() -> None:
    """Binder's environment.yml must not fork a second Python dependency set.

    It must install from requirements.txt rather than declaring its own list.
    It must NOT install from requirements-docker.lock: that lock pins
    `pywinpty==3.0.3` with no platform marker, a Windows-only wheel with no
    source distribution, which fails to build on Binder's Linux image.
    """
    config = yaml.safe_load(_read("environment.yml"))
    pip_section = next(dep["pip"] for dep in config["dependencies"] if isinstance(dep, dict))
    assert any("requirements.txt" in entry for entry in pip_section)
    assert not any("requirements-docker.lock" in entry for entry in pip_section)


def test_articles_code_tools_enabled_for_source_download() -> None:
    """`articles/` carries the reference Python implementations, so its pages
    need the source-download menu Quarto's `code-tools` provides. The site
    default is `code-tools: false` (_quarto.yml); this override must apply to
    the one directory that actually shows code.
    """
    config = yaml.safe_load(_read("articles/_metadata.yml"))
    assert config["format"]["html"]["code-tools"] is True


def test_root_quarto_default_is_still_code_tools_false() -> None:
    """The site-wide default stays off; only `articles/` opts in."""
    text = _read("_quarto.yml")
    assert re.search(r"^\s*code-tools:\s*false\s*$", text, flags=re.M)


def test_binder_launch_include_targets_the_notebooks_directory() -> None:
    """The shared Binder launch fragment must link mybinder.org at the
    notebook series directory so every chapter notebook is reachable.
    """
    fragment = _read(BINDER_INCLUDE)
    assert "mybinder.org" in fragment
    assert "notebooks/geometry_of_motion" in fragment


def test_every_book_includes_the_binder_launch_fragment() -> None:
    """Every book's Notebook Workflow section links the shared Binder launch,
    rather than each book duplicating its own copy of the URL.
    """
    for book in BOOK_FILES:
        text = _read(book)
        assert "{{< include ../_includes/notebook-binder-launch.qmd >}}" in text, book


def test_notebooks_readme_links_binder() -> None:
    """The notebooks series README is the other reader entry point besides
    the rendered book pages; it must offer the same Binder launch.
    """
    readme = _read("notebooks/geometry_of_motion/README.md")
    assert "mybinder.org" in readme


def test_root_hygiene_allows_the_new_environment_file() -> None:
    """The root-hygiene allowlist must be updated in the same change, or the
    new `environment.yml` file will fail `check_root_hygiene.py` in CI.
    """
    from scripts.check_root_hygiene import ALLOWED_TRACKED_ROOT_FILES

    assert "environment.yml" in ALLOWED_TRACKED_ROOT_FILES


def test_devcontainer_configuration_matches_spec() -> None:
    """The devcontainer config must exist, be valid JSON, build from the repo
    Dockerfile targeting 'dev', and specify repository root as context.
    """
    devcontainer_path = REPO_ROOT / ".devcontainer" / "devcontainer.json"
    assert devcontainer_path.is_file()
    data = json.loads(devcontainer_path.read_text(encoding="utf-8"))
    assert data["name"] == "AffineDrift"
    assert "build" in data
    assert data["build"]["dockerfile"] == "../Dockerfile"
    assert data["build"]["context"] == ".."
    assert data["build"]["target"] == "dev"
    assert data.get("forwardPorts") == [8000, 8888]


def test_root_hygiene_allows_devcontainer_directory() -> None:
    """The root-hygiene allowlist must permit the .devcontainer directory."""
    from scripts.check_root_hygiene import ALLOWED_TRACKED_ROOT_DIRECTORIES

    assert ".devcontainer" in ALLOWED_TRACKED_ROOT_DIRECTORIES
