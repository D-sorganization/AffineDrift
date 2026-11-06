# Quarto render check (Alpha War v1)

Local render (when Quarto is installed, e.g. CI dev Docker image):

```bash
CODECOV_TOKEN=unused quarto render research/alpha-war/draft/alpha-war-v1.md --to html
```

Automated guard: `python3 research/alpha-war/calcs/test_alpha_war_quarto_unpublished.py` (skips render if `quarto` is absent; always asserts `draft` / `listing: false` / `do-not-publish` and absence from `_quarto.yml`).

## Local render result (2026-11-06, Quarto 1.8.26, #5370)

`render-log.txt` is the log of the command above: exit 0, no `[WARNING]`, no unresolved
citation. Rendered HTML counts: 9 callout boxes (source has 9), 25 tables, 20 figures,
28 reference entries, about 1,670 math spans. The HTML output is not committed.

The site is untouched: the draft is not in `_quarto.yml` `project.render` and its directory is
not a sitemap source (`calcs/test_alpha_war_not_in_site_listing.py`). Changing publication
settings needs owner sign-off.
