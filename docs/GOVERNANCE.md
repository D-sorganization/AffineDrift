# Repository Governance Status

**Last Updated:** [Auto-generated on each governance workflow run]

## Approved Autonomous Agents

This repository supports the following autonomous agents:

- ✅ **claude** - Anthropic's Claude agents (approved for this repo)
- ✅ **maxwell-daemon** - Agent-agnostic delivery daemon (approved for this repo)
- ❓ **gaai** - Claude-only GAAI system (DEPRECATED - use Maxwell-Daemon instead)
- ❌ **codex** - Not approved for this repository
- ❌ **Other agents** - Require explicit authorization

## Governance Workflows Status

The following workflows provide protective governance:

| Workflow | Purpose | Status |
|----------|---------|--------|
| Jules-Redundant-PR-Closer.yml | Deduplicates agent PRs by priority | ✅ Active |
| Jules-Redundant-Issue-Closer.yml | Deduplicates agent issues by priority | ✅ Active |
| Agent-Governance-Check.yml | Enforces governance requirements | ✅ Active |

**Backup Schedule:**
- PR deduplication: Every PR event + 3-hourly automatic check
- Issue deduplication: Every issue event + 6-hourly automatic check
- Governance enforcement: Every PR modification

## Agent Priority Order

When multiple agents discover the same issue or PR at the same time, this priority order determines which agent's work is kept:

1. **user** - Manual PRs/issues (never auto-closed)
2. **maxwell-daemon** - Maxwell-Daemon system
3. **claude** - Anthropic's Claude agents
4. **codex** - Other code generation agents
5. **jules** - Jules coordination/repair bots
6. **local** - Local/CLI-triggered agents
7. **gaai** - GAAI system (deprecated)

*Higher priority agents' work is kept; lower priority duplicates are closed with a deferral comment.*

## Issue Claim Protocol

All autonomous agents MUST follow this protocol:

1. **Check claim status** before starting work:
   ```bash
   python -m scripts.check_agent_claim --issue <N>
   ```

2. **Post a lease** to claim the issue:
   ```bash
   python -m scripts.post_agent_lease --agent <id> --issue <N>
   ```

3. **Reference in PR** when submitting fix:
   ```
   Fixes #<N>
   ```

4. **Complete by merging** the PR - this automatically releases the claim.

**Why:** Prevents multiple agents from working on the same issue simultaneously.

## Fleet Coordination Rules

### For Agent Developers

- **Never assume** you're the only agent working on an issue
- **Always check** agent claim registry before starting work
- **Always reference** the issue number in your PR title
- **Expect deduplication** - if another agent was faster, your PR will be closed with deference
- **Monitor governance logs** in GitHub Actions for deduplication events

### For Repository Maintainers

- **Verify governance workflows** are active before enabling any agent
- **Monitor the governance dashboard** for repeated duplicates
- **Report issues** to Repository_Management if deduplication isn't working
- **Update GOVERNANCE.md** when agent priorities change

### For Fleet Coordinators

- **Monitor redundant-PR-closer logs** for patterns of duplicate work
- **Monitor redundant-issue-closer logs** for patterns of duplicate discovery
- **Adjust agent priorities** if certain agents consistently lose races
- **Update agent documentation** if coordination patterns change

## Troubleshooting

### Duplicate Issues Still Appearing

1. Check that Jules-Redundant-Issue-Closer.yml is active:
   ```bash
   gh workflow list -q '.[].name | select(. | contains("Redundant"))'
   ```

2. Check recent workflow runs:
   ```bash
   gh run list --workflow=Jules-Redundant-Issue-Closer.yml --limit 5
   ```

3. If workflow never runs, manually trigger it:
   ```bash
   gh workflow run "Agent Redundant Issue Closer" --ref main
   ```

### Duplicate PRs Not Being Closed

1. Check Jules-Redundant-PR-Closer.yml is active
2. Verify the PRs reference the same issue via "Fixes #N"
3. Check that closing agent has higher priority than affected PRs
4. Manually trigger if needed:
   ```bash
   gh workflow run "Agent Redundant PR Closer" --ref main
   ```

### New Agent Deployment

Before deploying a new autonomous agent to this repository:

1. **Verify governance workflows exist** and are active
2. **Run pre-deployment script**:
   ```bash
   bash Repository_Management/scripts/verify-governance.sh
   ```
3. **Add agent to approved list** in this GOVERNANCE.md
4. **Configure agent priority** in governance workflows if needed
5. **Document agent behavior** in repository documentation
6. **Start agent** with governance workflows active
7. **Monitor first 10 minutes** for duplicate issues/PRs

## Last Updated

Auto-updated by Agent-Governance-Check.yml and governance workflows.

Previous updates:
- [Timestamp of last governance workflow run]
- [Timestamp of last configuration change]
