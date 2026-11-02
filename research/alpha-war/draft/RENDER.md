# Quarto render check (Alpha War v0)

Local render (when Quarto is installed, e.g. CI dev Docker image):

```bash
quarto render research/alpha-war/draft/alpha-war-v0.md --to html \
  --output-dir research/alpha-war/draft/_render_check
```

Automated guard: `python3 research/alpha-war/calcs/test_alpha_war_quarto_unpublished.py` (skips render if `quarto` is absent; always asserts `draft` / `listing: false` / `do-not-publish` and absence from `_quarto.yml`).

This cloud agent run had no Quarto binary; attach CI or local `render-log.txt` after a successful render on a fleet runner.
