# Link Checker — `src.tools.check_links`

Single tool for link validation on AffineDrift. Two modes:

```bash
python3 -m src.tools.check_links                 # legacy broken-link scan
python3 -m src.tools.check_links --source-checks # site link quality gate (#3899)
```

The legacy scan validates `@sec-/@fig-/@eq-` cross-references' sibling concern —
internal links in scanned `.qmd`/`.html` files — and is also run by
`deploy-website.yml` after Quarto renders. The `--source-checks` gate (issue
#3899, wired into the `ci-standard.yml` quality-gate job) validates the
rendered source set declared by the root `_quarto.yml` `project.render` list.

## Source checks

1. **Internal link resolution** (`unresolved-internal-link`,
   `no_include_target`) — every relative `.html`/`.qmd`/asset link in a
   rendered source must resolve. Links inside files pulled in via
   ``{{< include path >}}`` resolve **against the including page's
   directory**, which is how Quarto renders them. This is the check that
   catches the #3906 monograph class: a chapter file whose `../figures/...`
   or `data/.../figures/...` embed resolves on its own directory but not
   from the page that includes it. Broken links have **no budget** — they
   always fail.
2. **Path-style normalization** (`root-absolute-link`, `qmd-extension-link`) —
   cross-page links must use the bare/parent-relative `.html` convention.
   Root-absolute targets (`/pages/x.html`) and `.qmd` targets are rejected.
   Files with accepted legacy violations are listed in the config allowlists.
3. **Related-coverage gate** (`related-missing`, `related-undersized`) — every
   content page carries the canonical Related Articles component (issue
   #3897: `## Related Articles` + `::: {.callout-note}` callout) with at
   least `min_links` resolving page links. The content universe is declared
   by `content_page_globs` (book-chapter interiors are excluded by
   construction); hub pages and allowlisted pages are exempt.
4. **Orphan detection** (`orphan-page`) — every rendered page needs
   in-degree >= 1 from content-page links, navigation (`href` and book
   `chapters` entries across every `_quarto.yml`, including nested book
   projects), or `{{< include >}}` edges. Hub pages are graph roots and
   always pass.

## Budget / baseline mechanism

Known violations that predate the gate are budgeted in
`config/link_checker_budget.json` (the repository's standard `config/`
budget pattern). Violations inside the budget are reported with counts;
violations beyond it fail the build. Ratchet the file down as drift is
fixed — never raise it to admit new violations.

| Key | Meaning |
|------|---------|
| `content_page_globs` | Pages the related-coverage gate applies to |
| `hub_pages` | Navigation/hub pages exempt from related coverage and the orphan gate |
| `related_coverage.min_links` | Required resolving links in the component (3) |
| `related_coverage.allowlist` | Content pages whose missing/undersized section is budgeted |
| `orphans.allowlist` | Rendered pages with in-degree 0 that are budgeted |
| `path_style.root_absolute_allowlist` | Files whose root-absolute page links are budgeted |
| `path_style.qmd_extension_allowlist` | Files whose `.qmd`-extension page links are budgeted |

Current budgeted baselines (ratchet targets, see the #3899 PR for detail):

- `related_coverage.allowlist` — 62 content pages without a canonical
  Related Articles section (follow-ups tracked by the #3896 child issues
  C4-C9; the six motor-control cluster pages are owned by the C5 effort).
- `orphans.allowlist` — 39 unreachable rendered pages (book-volume
  duplicates, tangent-hyperplane drafts, and a few nav-less pages).
- `path_style.qmd_extension_allowlist` — 11 files (17 links) still using
  `.qmd` link extensions.
- `path_style.root_absolute_allowlist` — only `_includes/home-sidebar-content.html`,
  whose links are root-absolute by necessity: one shared include renders at
  several directory depths, so a single relative form cannot serve all of them.

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | All checks pass, or every violation is inside its budget (baseline counts are logged) |
| `1` | At least one violation beyond budget (unresolved internal link, missing include target, unbudgeted path-style/related/orphan violation) |

Argparse usage errors exit `2` (standard library behavior). The legacy
scan exits `1` on any broken internal link and has no budget.