# Assessment M: Configuration

## Grade: A- (9/10)

## Analysis
Configuration is generally externalized and standard.

### Strengths
*   **Standard Files:** Uses `ruff.toml`, `pyproject.toml`, `_quarto.yml`.
*   **Env Vars:** CI workflows use secrets and env vars.

### Weaknesses
*   **Hardcoded Constants:** Some physics and site constants are hardcoded in python files.

## Recommendations
1.  **Central Config:** Move shared constants (like Gravity, Site URL) to a shared configuration module or YAML file.
