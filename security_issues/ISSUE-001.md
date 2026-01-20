---
title: "Security: S310 Audit url open in tools/verify_images.py"
labels: ["security", "jules:sentinel"]
---

## Vulnerability detected

**Severity:** MEDIUM
**Location:** `tools/verify_images.py:57`

### Details
Bandit flagged usage of `urllib.request.urlopen`:
```python
with urllib.request.urlopen(req, timeout=5) as response:  # noqa: S310
```

### Context
This line is marked with `# noqa: S310`. Project security policy permits S310 suppressions for verification tools.

### Recommended Action
Verify that the URL source is trusted or sanitized to prevent Server-Side Request Forgery (SSRF) or arbitrary file access. If confirmed safe and compliant with policy, this issue can be closed.
