# F-AD-027

**Collection-time hard imports of optional notebook tooling**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| ⬜ Low | hygiene | medium | S | proposed |

**Locations:** `tests/test_stub_notebooks.py:14`, `tests/test_stub_notebooks.py:16`

## Finding

- Severity: Low  - Category: hygiene
- Confidence: medium
- Location: tests/test_stub_notebooks.py:14-16; requirements.txt:14-16
- Evidence: collection needs `hypothesis`, `nbformat`, `nbclient`; `requirements.txt` has `jupyter==1.1.1`
  (which drags them in) — fine for CI but a developer with `pip install -e .` plus `pytest` gets a collection
  error, and `--co` dies on the first file so the count guard would report 0.
- Proposed change: `pytest.importorskip("nbclient")` in that module, or list the three explicitly.
- Effort: S

## Draft Pull Request

**Title:** `test(notebooks): importorskip optional notebook tooling at collection`

### Why This Matters (The Pitch)

A developer with only `pip install -e .` and pytest hits a collection error on missing `hypothesis`, `nbformat` or `nbclient`, and `--co` dies at the first file. Use `pytest.importorskip` or list the packages explicitly.

### Proposed PR Body

## Problem
`tests/test_stub_notebooks.py:14-16` hard-imports `hypothesis`, `nbformat` and `nbclient`; `requirements.txt:14-16` only gets them via `jupyter==1.1.1`.

## Change
- [ ] Use `pytest.importorskip("nbclient")` in that module, or list the three packages explicitly

## Verification
`pytest --co` succeeds in an environment without the notebook packages.

## Risk and Rollback
Test-only change; revert to roll back.

## Handoff
None

Refs: adversarial review 2026-10-16, F-AD-027

---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53f`. This is a proposal, not a verdict — verify the cited lines before acting._
