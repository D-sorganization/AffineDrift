# Public Site Verification

AffineDrift treats the deployed website as a revision-bound publication artifact. A successful
Quarto render is necessary, but it is not sufficient evidence that readers can use the site.

## Publication Contract

The deployment workflow must:

1. render the canonical Quarto sources with the pinned Quarto version;
2. run the post-build health, pruning, bundling, asset-sync, and minification steps;
3. generate `docs/public-site-manifest.json` from the deployable HTML inventory;
4. verify every manifest route at the required mobile and desktop viewports in both themes;
5. capture representative tablet and desktop screenshots; and
6. deploy only after the local artifact passes, then repeat the every-page verification against
   the revision-matched live manifest.

The manifest is the fail-closed contract. Its `source_revision` identifies the Git commit that
produced the site, `page_count` must equal the route inventory, and every route has a declared page
kind. The verifier rejects duplicate routes, incomplete matrices, missing or empty primary
content, missing canonical URLs, wrong theme state, invisible navigation, duplicate or below-fold
primary headings, heading-rank skips, unnamed buttons, missing image alternatives, untypeset
visible equations, horizontal overflow, fixed overlays on the title, console errors, page errors,
and required-resource failures.

## Local Verification

Run the build steps in the same order as `.github/workflows/deploy-website.yml`. After the deploy
artifact and manifest exist, serve `docs/` from the repository root:

```powershell
py -3 -m http.server 8000 --directory docs
```

In another terminal, run the exhaustive matrix:

```powershell
node scripts/verify-public-site.js `
  --base-url http://127.0.0.1:8000 `
  --manifest docs/public-site-manifest.json `
  --output artifacts/public-site-verification/local-every-page.json
```

Capture the representative tablet and desktop evidence with the same route and viewport arguments
defined in the deployment workflow. Verification JSON and screenshots belong under
`artifacts/public-site-verification/`; they are evidence artifacts, not canonical website sources.

## Source and Generated-File Ownership

Edit Quarto, CSS, JavaScript, and Python sources in their canonical root locations. Do not commit a
local `docs/` render to repair the site. The deployment workflow regenerates that artifact, checks
canonical-to-generated asset synchronization, and binds its public manifest to the exact commit.

The proximal-to-distal publication is a declared projection of its pinned UpstreamDrift authority.
Run `scripts/verify_proximal_distal_projection.py` before publication changes are accepted. A file
must be source-identical, covered by a declared adaptation, or rejected; silent drift is not an
allowed state.

## Human Review

Automated checks establish structural and behavioral invariants. A reviewer must still inspect the
representative screenshots in both themes and at every representative width. Review the home page,
an article, the projected monograph, a textbook, the books hub, resources, models, and the offline
page for hierarchy, reading measure, whitespace, contrast, navigation consistency, and content-first
responsive behavior.
