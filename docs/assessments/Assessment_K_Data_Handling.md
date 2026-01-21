# Assessment: Data Handling

## Grade: 8/10

## Analysis
Data is stored in `data/` as YAML/JSON, which is appropriate for a static site. Scripts process this data effectively.

### Strengths
- YAML/JSON for structured data.
- Clear separation of content and data.

### Weaknesses
- Validation of data schemas could be stricter (e.g., using Pydantic models for YAML loading).

## Recommendations
1. Introduce Pydantic for validating `data/` files during build.
