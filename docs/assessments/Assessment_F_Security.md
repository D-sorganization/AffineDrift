# Assessment F: Security

## Score: 8/10

## Analysis
Security posture is solid for a static site.
- **Dependencies**: Pinned versions in `requirements.txt`.
- **Secrets**: No obvious secrets committed.
- **Permissions**: CI workflows use standard permissions.

## Findings
- **Strengths**: Dependency pinning.
- **Weaknesses**: None significant for this type of project.

## Recommendations
- Continue using `bandit` or similar tools to scan for security issues.
