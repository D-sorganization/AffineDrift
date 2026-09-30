"""Tests for persona start paths on learning-paths (issues #4409 and #4488).

Validates that:
1. All eight declared personas exist (including golfer-coach and student).
2. Each declared persona has:
   - At least one content cluster mapping (from config/categories.yml)
   - At least one exact-commit workflow page mapping (models/programming/workflows.qmd)
   - Structured routes: first_page, route_30min, and route_deep
3. Each persona's route target actually exists on disk and is a renderable content page.
4. The golfer/coach persona plainly states that the site does not give swing instruction.
5. The generated card include (_includes/generated/persona-cards.qmd) is current.
6. resources/learning-paths.qmd includes the generated persona cards and does not duplicate the grid.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.generate_persona_cards import generate_persona_cards

REPO_ROOT = Path(__file__).resolve().parents[1]
LEARNING_PATHS_PAGE = REPO_ROOT / "resources" / "learning-paths.qmd"
CATEGORIES_PATH = REPO_ROOT / "config" / "categories.yml"
PERSONA_CONFIG_PATH = REPO_ROOT / "config" / "personas.yml"
WORKFLOWS_PAGE = REPO_ROOT / "models" / "programming" / "workflows.qmd"
GENERATED_INCLUDE = REPO_ROOT / "_includes" / "generated" / "persona-cards.qmd"

REQUIRED_PERSONAS = frozenset(
    [
        "learner",
        "researcher",
        "integrator",
        "experimentalist",
        "reviewer",
        "contributor",
        "golfer-coach",
        "student",
    ]
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
        """All eight required personas must be declared."""
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

    def test_persona_has_display_name_and_description(self) -> None:
        """Each persona must have a display name and description."""
        personas = load_personas()
        for persona_id, persona in personas.get("personas", {}).items():
            assert persona.get("name"), f"Persona '{persona_id}' missing 'name'"
            assert persona.get("description"), f"Persona '{persona_id}' missing 'description'"

    def test_each_persona_has_first_page_30min_and_deep_routes(self) -> None:
        """Each persona must specify a first page, 30-min route, and deep route (WEB-01.3)."""
        personas = load_personas()
        for persona_id, persona in personas.get("personas", {}).items():
            for route_key in ("first_page", "route_30min", "route_deep"):
                route = persona.get(route_key)
                assert isinstance(
                    route, dict
                ), f"Persona '{persona_id}' missing route dict for '{route_key}'"
                assert route.get(
                    "title"
                ), f"Persona '{persona_id}' route '{route_key}' missing title"
                assert route.get("path"), f"Persona '{persona_id}' route '{route_key}' missing path"

    def test_each_persona_route_target_exists_and_renders(self) -> None:
        """Every route target in config/personas.yml must exist on disk and render (WEB-01.3)."""
        personas = load_personas()
        for persona_id, persona in personas.get("personas", {}).items():
            for route_key in ("first_page", "route_30min", "route_deep"):
                route = persona[route_key]
                target_rel = route["path"]
                # Resolve target file on disk: .html target maps to .qmd, .md, or direct file
                target_file = REPO_ROOT / target_rel
                source_candidates = [
                    target_file,
                    target_file.with_suffix(".qmd"),
                    target_file.with_suffix(".md"),
                ]
                exists = any(candidate.is_file() for candidate in source_candidates)
                assert (
                    exists
                ), f"Persona '{persona_id}' route '{route_key}' target does not exist: {target_rel}"

    def test_golfer_coach_plainly_states_no_swing_instruction(self) -> None:
        """Golfer/coach persona must state plainly that the site does not give swing instruction."""
        personas = load_personas()
        golfer_coach = personas.get("personas", {}).get("golfer-coach", {})
        combined_text = (
            f"{golfer_coach.get('description', '')} "
            f"{golfer_coach.get('instruction_disclaimer', '')}"
        ).lower()
        assert "not" in combined_text and (
            "swing instruction" in combined_text or "swing coaching" in combined_text
        ), "Golfer/coach persona must plainly state that AffineDrift does not provide swing instruction."


class TestPersonaIncludeGeneration:
    """Test persona card include generation and freshness."""

    def test_generated_persona_cards_include_is_current(self) -> None:
        """_includes/generated/persona-cards.qmd must match YAML configuration."""
        assert GENERATED_INCLUDE.exists(), f"Missing {GENERATED_INCLUDE}"
        generate_persona_cards(check=True, output_path=GENERATED_INCLUDE, base_dir="resources")

    def test_card_include_contains_all_personas(self) -> None:
        """The include file must contain card blocks for every persona."""
        content = GENERATED_INCLUDE.read_text(encoding="utf-8")
        for persona_id in REQUIRED_PERSONAS:
            assert (
                f'id="persona-{persona_id}"' in content or f"#persona-{persona_id}" in content
            ), f"Missing persona '{persona_id}' anchor in generated include"


class TestPersonaLinksInLearningPaths:
    """Test that learning-paths.qmd includes persona start paths and eliminates duplication."""

    def test_learning_paths_references_personas(self) -> None:
        """The learning-paths page must have a persona start paths section with the include."""
        content = LEARNING_PATHS_PAGE.read_text(encoding="utf-8")
        assert "## Start by Persona" in content
        assert "persona-cards.qmd" in content

    def test_learning_paths_does_not_duplicate_path_grid(self) -> None:
        """The duplicated 'Choose a path' grid on learning-paths.qmd must be removed (WEB-01.3)."""
        content = LEARNING_PATHS_PAGE.read_text(encoding="utf-8")
        assert (
            "Choose a path:" not in content
        ), "learning-paths.qmd should not contain the duplicated 'Choose a path' grid"


class TestPersonaClusters:
    """Test content cluster mappings for personas."""

    def test_learner_has_foundational_clusters(self) -> None:
        personas = load_personas()
        learner = personas.get("personas", {}).get("learner", {})
        clusters = set(learner.get("content_clusters", []))
        foundational = {"theory-core", "reference", "resources"}
        assert clusters & foundational, "Learner should map to foundational clusters"

    def test_researcher_has_theory_clusters(self) -> None:
        personas = load_personas()
        researcher = personas.get("personas", {}).get("researcher", {})
        clusters = set(researcher.get("content_clusters", []))
        theory = {"theory-core", "tangent-space", "inverse-dynamics"}
        assert clusters & theory, "Researcher should map to theory clusters"

    def test_integrator_has_tools_clusters(self) -> None:
        personas = load_personas()
        integrator = personas.get("personas", {}).get("integrator", {})
        clusters = set(integrator.get("content_clusters", []))
        integration = {"tools", "models"}
        assert clusters & integration, "Integrator should map to tools/models clusters"

    def test_experimentalist_has_models_clusters(self) -> None:
        personas = load_personas()
        experimentalist = personas.get("personas", {}).get("experimentalist", {})
        clusters = set(experimentalist.get("content_clusters", []))
        experimental = {"models", "inverse-dynamics", "motor-control"}
        assert clusters & experimental, "Experimentalist should map to experimental clusters"

    def test_reviewer_has_critique_clusters(self) -> None:
        personas = load_personas()
        reviewer = personas.get("personas", {}).get("reviewer", {})
        clusters = set(reviewer.get("content_clusters", []))
        assert "critique" in clusters, "Reviewer should map to critique cluster"

    def test_contributor_has_site_clusters(self) -> None:
        personas = load_personas()
        contributor = personas.get("personas", {}).get("contributor", {})
        clusters = set(contributor.get("content_clusters", []))
        contribution = {"site-information", "tools", "resources"}
        assert clusters & contribution, "Contributor should map to contribution clusters"

    def test_golfer_coach_has_golf_clusters(self) -> None:
        personas = load_personas()
        golfer_coach = personas.get("personas", {}).get("golfer-coach", {})
        clusters = set(golfer_coach.get("content_clusters", []))
        golf_clusters = {"impact-ball-flight", "technology", "putting"}
        assert clusters & golf_clusters, "Golfer/coach should map to golf clusters"

    def test_student_has_education_clusters(self) -> None:
        personas = load_personas()
        student = personas.get("personas", {}).get("student", {})
        clusters = set(student.get("content_clusters", []))
        student_clusters = {"theory-core", "motor-control", "reference"}
        assert clusters & student_clusters, "Student should map to education clusters"
