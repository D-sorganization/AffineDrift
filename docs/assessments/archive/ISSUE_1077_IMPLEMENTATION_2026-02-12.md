# Issue 1077 Implementation - Technical Debt Guardrails

Date: 2026-02-12
Issue: https://github.com/D-sorganization/AffineDrift/issues/1077

## Delivered

- Added budget config:
  - `config/tech_debt_budget.json`
- Added enforcement script:
  - `scripts/check_tech_debt_budget.py`
- Integrated into CI and deploy workflows:
  - `.github/workflows/ci-standard.yml`
  - `.github/workflows/deploy-website.yml`

## Why This Addresses the Issue

Issue `#1077` identified uncontrolled debt growth (`TODO`/`FIXME`/`HACK` patterns) and process bypass risk.
This implementation adds an enforceable baseline budget that blocks net growth in marker debt during PR validation.

## Validation

```bash
python3 scripts/check_tech_debt_budget.py
```
