# GitHub Repository Protection & CI/CD Guide

## Branch Protection Rules

To protect the main branch and ensure quality control, configure these protection rules:

### Setting Up Branch Protection

1. **Navigate to Settings**

   - Go to repository → Settings → Branches
   - Click "Add rule" or edit existing rule for `main`

2. **Required Protection Rules**

   ✅ **Require pull request reviews before merging**

   - Minimum 1 approval required (or self-review for solo projects)
   - Dismiss stale pull request approvals when new commits are pushed

   ✅ **Require status checks to pass before merging**

   - Require branches to be up to date before merging
   - Status checks that should pass:
     - `validate` (HTML/CSS validation)
     - `build-deploy` (Quarto build succeeds)

   ✅ **Require conversation resolution before merging**

   - All comments must be resolved

   ✅ **Require linear history**

   - Prevents merge commits, enforces clean history
   - Use squash or rebase merge

   ✅ **Include administrators**

   - Apply rules to repository administrators too

   ✅ **Restrict who can push to matching branches**

   - Only allow specific users/teams to push directly
   - Or: disable direct pushes entirely (force PRs)

3. **Optional but Recommended**

   - **Require signed commits**: Verify commit authenticity
   - **Require deployments to succeed**: Before merging to production
   - **Lock branch**: Prevent all changes (for release branches)

### Example Configuration

```yaml
Protection Rules for 'main':
├── Require pull request before merging: ✓
│   ├── Required approvals: 1
│   └── Dismiss stale reviews: ✓
├── Require status checks: ✓
│   ├── validate (HTML/CSS)
│   ├── build-deploy (Quarto)
│   └── Require up-to-date: ✓
├── Require conversation resolution: ✓
├── Require linear history: ✓
├── Include administrators: ✓
└── Restrict pushes: ✓ (GitHub Actions only)
```

## CI/CD Workflows

### Current Workflows

#### 1. **Static Site Deployment** (`.github/workflows/deploy.yml`)

- **Triggers**: Push to main, PRs
- **Jobs**:
  - Validate HTML/CSS
  - Check for common issues
  - Deploy to GitHub Pages (main only)
  - Run accessibility tests (PRs only)

#### 2. **Quarto Publishing** (`.github/workflows/quarto-publish.yml`)

- **Triggers**: Push to main, PRs, manual
- **Jobs**:
  - Install Quarto
  - Render entire project
  - Deploy to GitHub Pages

### Best Practices

#### Status Checks

All PRs should pass these checks before merging:

- ✅ HTML validation
- ✅ CSS linting
- ✅ Build succeeds (no errors)
- ✅ Accessibility checks (warnings OK)

#### Review Process

1. Create feature branch from main
2. Make changes
3. Open pull request
4. Wait for CI checks to pass
5. Request review (if team)
6. Address feedback
7. Squash and merge

#### Deployment Strategy

**Main Branch:**

- Protected, requires PR
- Auto-deploys on merge
- Always production-ready

**Feature Branches:**

- Claude branches: `claude/*`
- Personal branches: `feature/*`, `fix/*`
- Preview builds in PR (optional)

## Security Considerations

### Secrets Management

- Never commit API keys, tokens, or passwords
- Use GitHub Secrets for sensitive data
- Rotate credentials regularly

### Dependabot

Enable Dependabot for:

- Security updates
- Version updates
- GitHub Actions updates

### Code Scanning

Consider enabling:

- **CodeQL**: Automated code security scanning
- **Secret scanning**: Detect committed secrets
- **Dependency review**: Review new dependencies

## Repository Settings Checklist

### General

- [ ] Set repository visibility (Public recommended for GitHub Pages)
- [ ] Add description and topics
- [ ] Include README.md
- [ ] Add LICENSE file

### Branches

- [ ] Set default branch to `main`
- [ ] Configure branch protection rules
- [ ] Enable delete head branches automatically

### Pages

- [ ] Enable GitHub Pages
- [ ] Source: GitHub Actions
- [ ] Custom domain: affinedrift.com (configured)
- [ ] Enforce HTTPS: ✓

### Actions

- [ ] Allow all actions (needed for Quarto)
- [ ] Workflow permissions: Read and write
- [ ] Enable Actions cache

### Security

- [ ] Enable Dependabot alerts
- [ ] Enable Dependabot security updates
- [ ] Enable secret scanning (if available)
- [ ] Enable code scanning (if available)

### Collaborators & Teams

- [ ] Add collaborators as needed
- [ ] Set appropriate permissions
- [ ] Configure team access (if organization)

## Monitoring & Maintenance

### Regular Tasks

- **Weekly**: Review Dependabot alerts
- **Monthly**: Check Actions usage/costs
- **Quarterly**: Review and update dependencies
- **Annually**: Review all settings and permissions

### Metrics to Monitor

- Build success rate
- Deployment frequency
- PR review time
- CI/CD duration
- Site performance

## Emergency Procedures

### If Main Branch is Broken

1. Revert the breaking commit
2. Push revert to main (emergency bypass protection if needed)
3. Fix issue in separate branch
4. Create PR with fix
5. Merge after CI passes

### If CI/CD Fails

1. Check GitHub Actions status page
2. Review workflow run logs
3. Test locally: `quarto render`
4. Check for missing files/dependencies
5. Contact GitHub support if platform issue

## Recommended Tools

### Local Development

- **Quarto CLI**: Site building and preview
- **VS Code**: Code editing with extensions
- **Git**: Version control
- **Python 3.11+**: For conversion scripts

### Browser Extensions

- **GitHub Dark Mode**: Easier reading
- **Octotree**: Repository tree view
- **Refined GitHub**: UI improvements

### VS Code Extensions

- **Quarto**: Syntax highlighting and preview
- **GitLens**: Enhanced git features
- **Markdown All in One**: Markdown editing
- **Python**: Python development

## Additional Resources

- [GitHub Branch Protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Quarto CI/CD](https://quarto.org/docs/publishing/github-pages.html)
- [GitHub Pages](https://docs.github.com/en/pages)

---

**Last Updated**: 2025-11-26
**Maintained By**: Dieter Olson
