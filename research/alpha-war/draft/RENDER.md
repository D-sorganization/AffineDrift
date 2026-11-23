# Quarto render check (Alpha War v1)

Local render (when Quarto is installed, e.g. CI dev Docker image):

```bash
CODECOV_TOKEN=unused quarto render research/alpha-war/draft/alpha-war-v1.md --to html
```

Automated guard: `python3 -m unittest test_alpha_war_quarto_unpublished` in `research/alpha-war/calcs/` (skips the HTML render step only if `quarto` is absent locally; always asserts `draft` / `listing: false` / `do-not-publish` and absence from `_quarto.yml`).

CI: workflow **Alpha War Draft Quarto** (`.github/workflows/alpha-war-draft-quarto.yml`) runs the full module—including `test_optional_quarto_render`—on PRs that touch the draft or Quarto guard tests (#5370).
