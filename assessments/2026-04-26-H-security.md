# Criterion H: Security

**Repo:** AffineDrift
**Score:** 59/100
**Weight:** 10%
**Weighted Contribution:** 5.90

## Evidence

```json
{
  "secrets_raw": 12
}
```

## Findings

### P0: [AffineDrift] 12 potential hardcoded secrets

Audit src/ for hardcoded credentials. Move to environment variables or secret manager.
