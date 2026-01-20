# Assessment: API Design

## Grade: 8/10

## Analysis
While primarily a website, the internal tools exhibit good design principles.
- **Modularity**: Functions in `tools/` are generally small and focused.
- **Interfaces**: Streamlit apps provide a visual interface to math models.

## Strengths
- Functional approach in `tools/wrist_universal_joint`.
- Clear inputs/outputs for Python scripts.

## Weaknesses
- Some coupling between Streamlit UI code and math logic (partially addressed in tests by copying).

## Improvement Plan
- Extract pure math logic from Streamlit apps into a shared `pymath` library to avoid duplication in tests.
