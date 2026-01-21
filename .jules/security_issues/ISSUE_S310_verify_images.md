# [Security] Medium Severity: Audit url open in `tools/verify_images.py`

**Labels:** `security`, `jules:sentinel`

## Description
Bandit security scan identified a Medium severity issue (S310) in `tools/verify_images.py` at line 57.

**Issue Text:** Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.

The code uses `urllib.request.urlopen` which supports `file://` schemes by default. If the URL input is influenced by an attacker, this could lead to Local File Inclusion (LFI) or Server-Side Request Forgery (SSRF).

**Vulnerable Code:**
```python
57:             with urllib.request.urlopen(req, timeout=5) as response:  # noqa: S310
```

## Remediation
Validate the URL scheme to ensure it is strictly `http` or `https` before making the request.

**Suggested Fix:**
```python
from urllib.parse import urlparse

parsed = urlparse(url)
if parsed.scheme not in ['http', 'https']:
    raise ValueError(f"Unsupported scheme: {parsed.scheme}")

with urllib.request.urlopen(req, timeout=5) as response:
    ...
```
