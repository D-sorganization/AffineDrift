# Site Release and Rollback

Operational procedures for publishing the AffineDrift Quarto site to GitHub Pages and recovering from a bad deploy.

## Release Path

1. Merge to `main` with a green `quality-gate` on the pull request and merge queue.
2. `deploy-website.yml` runs on every push to `main` (concurrency group keeps one publish in flight).
3. The workflow renders with the pinned Quarto version in `.quarto-version`, syncs frontend assets, runs claim-audit enforcement, and uploads the `_site/` artifact to GitHub Pages.
4. Confirm success:
   ```bash
   gh run list --repo D-sorganization/AffineDrift --workflow deploy-website.yml --limit 3
   ```
5. Spot-check the live site (`https://affinedrift.com`) using the post-deploy checklist in [post-deploy-verification.md](./post-deploy-verification.md).

## Rollback

GitHub Pages serves the last successful deploy until a new one completes. To roll back content:

1. Identify the last known-good commit on `main`:
   ```bash
   gh run list --workflow deploy-website.yml --json conclusion,headSha,createdAt --limit 10
   ```
2. Revert the offending merge on `main` with a normal revert pull request (do not bypass branch protection or use admin merge).
3. After the revert lands, `deploy-website.yml` republishes from the reverted tree automatically.
4. Run the post-deploy verification checklist on the restored site.

For incident triage steps (build failures, partial deploys), see [incident-response-playbooks.md](./incident-response-playbooks.md) and [on-call-procedures.md](./on-call-procedures.md).

## Related Issues

- Parent epic: #5321 (static publishing hardening)
- Post-deploy checks: #5320
