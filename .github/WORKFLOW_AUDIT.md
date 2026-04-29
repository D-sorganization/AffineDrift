# CI/CD Workflow Audit & Consolidation Plan

**Status:** In Progress  
**Date:** 2026-04-28  
**Related Issue:** #2915 (Consolidate and audit 21 CI/CD workflow files)  
**Related Epic:** #2873 (P0 CI health - 42 workflow files)

## Executive Summary

The repository has 19 workflow files (counted in 2026-04-28). This is excessive and
creates maintenance burden. The goal is to consolidate to 3-5 core workflows that cover:

1. **CI/Testing** - linting, tests, coverage checks
2. **Deployment** - production deployments
3. **Specification Validation** - spec checks
4. (Optional) **Performance** - benchmarks and monitoring
5. (Optional) **Documentation** - site generation and publishing

## Current Workflows

| Filename                        | Purpose                        | Status    | Priority         |
| ------------------------------- | ------------------------------ | --------- | ---------------- |
| ci-standard.yml                 | Core CI (lint, test, coverage) | CORE      | P0 - KEEP        |
| deploy-website.yml              | Website deployment             | CORE      | P0 - KEEP        |
| spec-check.yml                  | Specification validation       | CORE      | P0 - KEEP        |
| quarto-syntax-check.yml         | Quarto markdown validation     | Optional  | P1 - Review      |
| compile-textbooks.yml           | Build textbook outputs         | Optional  | P1 - Review      |
| stale-cleanup.yml               | Stale issue management         | Optional  | P1 - Consider    |
| Code-Metrics.yml                | Code quality metrics           | Duplicate | P2 - Consolidate |
| Pragmatic-Programmer-Review.yml | Policy enforcement             | Duplicate | P2 - Consolidate |
| Bot-CI-Trigger.yml              | CI triggering                  | Utility   | P2 - Remove      |
| ci-failure-digest.yml           | Failure notifications          | Utility   | P2 - Consolidate |
| Comment-to-Issue-Converter.yml  | Automation                     | Utility   | P2 - Review      |
| PR-Comment-Responder.yml        | Automation                     | Utility   | P2 - Review      |
| compile-golf-textbook.yml       | Specialty build                | Optional  | P1 - Review      |
| latex-release-volumes.yml       | LaTeX builds                   | Optional  | P1 - Review      |
| Manual-Run-All.yml              | Manual trigger                 | Utility   | P2 - Remove      |
| pr-auto-labeler.yml             | PR automation                  | Utility   | P1 - Keep        |
| publish-textbooks-on-merge.yml  | Publishing                     | Specialty | P1 - Keep        |
| quarto-pdf-render.yml           | PDF generation                 | Specialty | P1 - Review      |
| Maintenance-Global-Control.yml  | Maintenance                    | Utility   | P2 - Review      |

## Consolidation Plan

### Phase 1: Core Workflows (No Changes)

These three workflows are essential and should be kept as-is:

1. **ci-standard.yml** - All testing, linting, coverage
2. **deploy-website.yml** - Production website deployment
3. **spec-check.yml** - Specification validation

### Phase 2: Optional Workflows (Keep/Review/Merge)

Keep only if actively used:

- **pr-auto-labeler.yml** - Low cost, high value → KEEP
- **publish-textbooks-on-merge.yml** - Core functionality → KEEP
- **quarto-syntax-check.yml** - Can be merged into ci-standard.yml → CONSOLIDATE
- **compile_textbooks.yml** - Can be merged into deploy-website.yml → CONSOLIDATE

### Phase 3: Duplicate Workflows (Consolidate)

These overlap with core workflows and should be merged:

- **Code-Metrics.yml** → Merge into ci-standard.yml
- **Pragmatic-Programmer-Review.yml** → Merge into ci-standard.yml
- **ci-failure-digest.yml** → Merge into ci-standard.yml (notifications)

### Phase 4: Utility Workflows (Remove/Consolidate)

These add little value or can be replaced:

- **Bot-CI-Trigger.yml** → Remove (duplicates other triggers)
- **Manual-Run-All.yml** → Remove (redundant)
- **Comment-to-Issue-Converter.yml** → Review for value (consider removal)
- **PR-Comment-Responder.yml** → Review for value (consider removal)
- **Maintenance-Global-Control.yml** → Document or remove

### Phase 5: Specialty Workflows (Document or Consolidate)

Keep only if necessary for the project's unique needs:

- **compile-golf-textbook.yml** → Keep (specialty) or consolidate
- **latex-release-volumes.yml** → Keep (specialty) or consolidate
- **quarto-pdf-render.yml** → Keep (specialty) or consolidate

## Target State

After consolidation, target workflows:

```
.github/workflows/
├── ci-standard.yml            # Lint, test, coverage, code metrics, specs
├── deploy-website.yml         # Website deployment and textbook publishing
├── pr-auto-labeler.yml        # PR automation (low cost)
├── (optional) specialty.yml   # Textbook compilation (if needed)
└── README.md                  # Workflow documentation
```

**Result: 4 core workflows** (down from 19)

## Implementation Steps

### Step 1: Document Current Behavior

- [ ] List all workflows and their triggers
- [ ] Document what each workflow actually does
- [ ] Identify overlaps and dependencies
- [ ] Interview team about which workflows are critical

### Step 2: Create Merged Workflows

- [ ] Combine code-metrics into ci-standard.yml
- [ ] Combine quarto-syntax-check into ci-standard.yml
- [ ] Test merged workflows in a feature branch

### Step 3: Cleanup Phase

- [ ] Delete or disable low-value utility workflows
- [ ] Archive specialty workflows if not needed
- [ ] Document why each workflow was kept or removed

### Step 4: Documentation

- [ ] Create .github/workflows/README.md explaining each workflow
- [ ] Update CONTRIBUTING.md with CI/CD expectations
- [ ] Document workflow trigger conditions

### Step 5: Verification

- [ ] Run full CI suite on test PR
- [ ] Verify all status checks pass
- [ ] Confirm critical workflows still trigger
- [ ] Monitor for regressions post-consolidation

## Success Criteria

- [ ] Reduced from 19 to 4-5 workflows
- [ ] All critical functions still work
- [ ] Faster overall CI execution (eliminated redundancy)
- [ ] Clearer workflow responsibilities documented
- [ ] No functionality lost in consolidation
- [ ] Team understands purpose of each remaining workflow

## Timeline

| Phase                   | Timeline | Owner       |
| ----------------------- | -------- | ----------- |
| Phase 1: Audit          | 1-2 days | QA/DevOps   |
| Phase 2: Planning       | 1-2 days | Team review |
| Phase 3: Implementation | 3-5 days | DevOps      |
| Phase 4: Testing        | 2-3 days | QA          |
| Phase 5: Documentation  | 1-2 days | Tech Writer |

**Total: 8-14 days**

## Risks & Mitigations

| Risk              | Mitigation                                                   |
| ----------------- | ------------------------------------------------------------ |
| Breaking CI/CD    | Keep changes in feature branch, test thoroughly before merge |
| Missing workflows | Document current state before making changes                 |
| Knowledge loss    | Document why each workflow exists before removing it         |
| Team disruption   | Communicate plan and impact clearly to all stakeholders      |

## References

- [GitHub Actions: Workflow syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [GitHub Actions: Reusable workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [Best practices for GitHub Actions](https://docs.github.com/en/actions/guides/index)

## Related Issues

- #2915: Consolidate and audit 21 CI/CD workflow files (P0)
- #2873: Mixed CI health with 42 workflow files (P0)
- #2889: Assessment Epic - 2026-04-26 A–O Health Assessment
