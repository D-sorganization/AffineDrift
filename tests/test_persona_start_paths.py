"""Tests for persona start paths on learning-paths (issue #4409).

Validates that each declared persona has:
- At least one content cluster mapping (from config/categories.yml)
- At least one exact-commit workflow page mapping (models/programming/workflows.qmd)
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
LEARNING_PATHS_PAGE = REPO_ROOT / "resources" / "learning-paths.qmd"
CATEGORIES_PATH = REPO_ROOT / "config" / "categories.yml"
PERSONA_CONFIG_PATH = REPO_ROOT / "config" / "personas.yml"
WORKFLOWS_PAGE = REPO_ROOT / "models" / "programming" / "workflows.qmd"

REQUIRED_PERSONAS = frozenset(
    ["learner", "researcher", "integrator", "experimentalist", "reviewer", "contributor"]
)


def load_personas() -> dict:
    """Load persona configuration from config/personas.yml."""
    if not PERSONA_CONFIG_PATH.exists():
        pytest.skip("config/personas.yml not yet created")
    return yaml.safe_load(PERSONA_CONFIG_PATH.read_text(encoding="utf-8"))


def load_categories() -> set[str]:
    """Load controlled category vocabulary."""
    if not CATEGORIES_PATH.exists():
        pytest.skip("config/categories.yml not found")
    data = yaml.safe_load(CATEGORIES_PATH.read_text(encoding="utf-8"))
    return set(data.keys())


def extract_workflow_ids() -> set[str]:
    """Extract workflow IDs from the workflows page."""
    if not WORKFLOWS_PAGE.exists():
        pytest.skip("models/programming/workflows.qmd not found")
    content = WORKFLOWS_PAGE.read_text(encoding="utf-8")
    ids = set()
    for line in content.splitlines():
        if line.startswith("| `") and "`" in line[3:]:
            workflow_id = line[3 : line.index("`", 3)]
            if workflow_id:
                ids.add(workflow_id)
    return ids


class TestPersonaConfiguration:
    """Test that persona configuration is complete and valid."""

    def test_personas_config_exists(self) -> None:
        """Persona configuration file must exist."""
        assert PERSONA_CONFIG_PATH.exists(), f"Missing {PERSONA_CONFIG_PATH}"

    def test_all_required_personas_declared(self) -> None:
        """All six required personas must be declared."""
        personas = load_personas()
        declared = set(personas.get("personas", {}).keys())
        missing = REQUIRED_PERSONAS - declared
        assert not missing, f"Missing required personas: {missing}"

    def test_each_persona_has_content_clusters(self) -> None:
        """Each persona must map to at least one content cluster."""
        personas = load_personas()
        categories = load_categories()
        for persona_id, persona in personas.get("personas", {}).items():
            clusters = persona.get("content_clusters", [])
            assert clusters, f"Persona '{persona_id}' has no content_clusters"
            for cluster in clusters:
                assert (
                    cluster in categories
                ), f"Persona '{persona_id}' references unknown category '{cluster}'"

    def test_each_persona_has_workflow_pages(self) -> None:
        """Each persona must map to at least one exact-commit workflow page."""
        personas = load_personas()
        workflow_ids = extract_workflow_ids()
        for persona_id, persona in personas.get("personas", {}).items():
            workflows = persona.get("workflows", [])
            assert workflows, f"Persona '{persona_id}' has no workflows"
            for workflow in workflows:
                assert (
                    workflow in workflow_ids
                ), f"Persona '{persona_id}' references unknown workflow '{workflow}'"

    def test_persona_has_display_name(self) -> None:
        """Each persona must have a display name."""
        personas = load_personas()
        for persona_id, persona in personas.get("personas", {}).items():
            assert persona.get("name"), f"Persona '{persona_id}' missing 'name'"

    def test_persona_has_description(self) -> None:
        """Each persona must have a description."""
        personas = load_personas()
        for persona_id, persona in personas.get("personas", {}).items():
            assert persona.get("description"), f"Persona '{persona_id}' missing 'description'"


class TestPersonaLinksInLearningPaths:
    """Test that learning-paths.qmd includes persona start paths."""

    def test_learning_paths_references_personas(self) -> None:
        """The learning-paths page must have a persona start paths section."""
        content = LEARNING_PATHS_PAGE.read_text(encoding="utf-8")
        assert "persona" in content.lower(), "learning-paths.qmd missing persona section"

    def test_learning_paths_links_to_workflows(self) -> None:
        """The learning-paths page must link to programming workflows."""
        content = LEARNING_PATHS_PAGE.read_text(encoding="utf-8")
        assert (
            "models/programming/" in content or "workflows" in content.lower()
        ), "learning-paths.qmd must link to programming workflow pages"


class TestPersonaClusters:
    """Test content cluster mappings for personas."""

    def test_learner_has_foundational_clusters(self) -> None:
        """Learner persona should map to foundational content."""
        personas = load_personas()
        learner = personas.get("personas", {}).get("learner", {})
        clusters = set(learner.get("content_clusters", []))
        foundational = {"theory-core", "reference", "resources"}
        assert clusters & foundational, "Learner should map to foundational clusters"

    def test_researcher_has_theory_clusters(self) -> None:
        """Researcher persona should map to theory content."""
        personas = load_personas()
        researcher = personas.get("personas", {}).get("researcher", {})
        clusters = set(researcher.get("content_clusters", []))
        theory = {"theory-core", "tangent-space", "inverse-dynamics"}
        assert clusters & theory, "Researcher should map to theory clusters"

    def test_integrator_has_tools_clusters(self) -> None:
        """Integrator persona should map to tools and models."""
        personas = load_personas()
        integrator = personas.get("personas", {}).get("integrator", {})
        clusters = set(integrator.get("content_clusters", []))
        integration = {"tools", "models"}
        assert clusters & integration, "Integrator should map to tools/models clusters"

    def test_experimentalist_has_models_clusters(self) -> None:
        """Experimentalist persona should map to simulation content."""
        personas = load_personas()
        experimentalist = personas.get("personas", {}).get("experimentalist", {})
        clusters = set(experimentalist.get("content_clusters", []))
        experimental = {"models", "inverse-dynamics", "motor-control"}
        assert clusters & experimental, "Experimentalist should map to experimental clusters"

    def test_reviewer_has_critique_clusters(self) -> None:
        """Reviewer persona should map to critique content."""
        personas = load_personas()
        reviewer = personas.get("personas", {}).get("reviewer", {})
        clusters = set(reviewer.get("content_clusters", []))
        assert "critique" in clusters, "Reviewer should map to critique cluster"

    def test_contributor_has_site_clusters(self) -> None:
        """Contributor persona should map to site and tools content."""
        personas = load_personas()
        contributor = personas.get("personas", {}).get("contributor", {})
        clusters = set(contributor.get("content_clusters", []))
        contribution = {"site-information", "tools", "resources"}
        assert clusters & contribution, "Contributor should map to contribution clusters"
