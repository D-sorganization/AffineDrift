# Post-Deploy Verification

Checklist after `deploy-website.yml` succeeds or after a rollback redeploy (#5320).

## Automated Gates (CI / Deploy Workflow)

These run before Pages publish on `main`:

| Step | Script / workflow | Purpose |
| --- | --- | --- |
| Claim audit | `python3 -m scripts.generate_claim_audit_inventory --manifest _site/public-site-manifest.json --check --enforce-publication` | Every rendered route has audit coverage |
| Third-party SRI | `python3 -m scripts.post_render_sri_audit` | External scripts in `_site/` carry Subresource Integrity where required |
| Site manifest | `python3 scripts/public_site_manifest.py` | Canonical route list for audits |

## Manual / On-Demand Checks

From a machine with the repo and Python 3.12:

```bash
python3 src/tools/check_site_health.py
python3 -m src.tools.check_links
python3 src/tools/check_redirects.py
```

Record the deploy commit SHA from GitHub Actions and attach it to any incident thread.

## URL and Asset Integrity

- Compare `_site/build-provenance.json` (written during Docker/production builds) with the deployed commit when investigating drift.
- Regenerate the verifiable build manifest locally with `python3 -m scripts.write_build_manifest --check` (#5319).

## Related

- [site-release-rollback.md](./site-release-rollback.md)
- [static-publishing-hardening.md](./static-publishing-hardening.md)
