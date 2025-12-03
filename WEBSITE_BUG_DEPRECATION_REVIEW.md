# Website Bug & Deprecation Review

## Summary
This review records fixes for previously reported navigation typos, legacy JavaScript, and empty placeholder pages.

## Resolved Findings

### Pinocchio navigation spelling and repository link
- Navbar and model listing now use the correct "Pinocchio" spelling and link to the `Pinocchio_Golf_Model` repository to avoid mixed branding and potential 404s. The dedicated model page filename has been updated to match.

### Legacy navigation JavaScript mismatch
- The custom navigation helpers in `script.js` now target Quarto's Bootstrap navbar classes and rely on the built-in collapse behavior, removing unused logic that referenced a non-existent `.top-nav .nav-links` structure.

### Legacy placeholder pages shipped as blank HTML
- `legacy-pages/qmd/mujoco-demo.html` and `legacy-pages/qmd/reading-list.html` now display archived notices with links back to current content instead of rendering empty screens.

## Next Steps
- Rebuild the site to publish the corrected Pinocchio page name and archived legacy notices.
- Remove any stale links to the old `models-pinocchio.html` path once redirects or rebuilds are in place.
