---
title: "Critical Incomplete: Maintenance Workflows Disabled"
labels: incomplete-implementation, critical
---
# Critical Incomplete: Maintenance Workflows Disabled

**Priority**: High
**Status**: Open

## Description
Critical maintenance workflows are currently disabled due to pending API migration, blocking automated repository health checks and conflict resolution.

## Locations
1. **`.github/workflows/Jules-Tech-Custodian.yml`**: Disabled (`if: false`). Note: `TODO: Jules CLI API changed in v0.1.x`.
2. **`.github/workflows/Jules-Conflict-Fix.yml`**: Disabled. Note: `TODO: Jules CLI API changed in v0.1.x - needs migration`.

## Remediation
- **Immediate**: Update workflow files to match the new Jules CLI v0.1.x arguments and syntax.
- **Verification**: Re-enable workflows and verify successful execution.
