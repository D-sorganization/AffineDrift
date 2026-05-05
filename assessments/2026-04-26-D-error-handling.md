# Criterion D: Error Handling

**Repo:** AffineDrift
**Score:** 73.2/100
**Weight:** 10%
**Weighted Contribution:** 7.32

## Evidence

```json
{
  "bare_except": 6,
  "except_exception": 3,
  "noqa_suppressions": 133
}
```

## Findings

### P1: [AffineDrift] 6 bare except: statements

Replace bare `except:` with specific exception types.

### P1: [AffineDrift] 133 lint suppressions

High suppression count indicates over-suppression or real code quality issues.
