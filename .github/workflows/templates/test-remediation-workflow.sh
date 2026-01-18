#!/bin/bash
# Test script for Jules Assessment Remediator workflow
# This script helps validate the workflow configuration and test it in dry-run mode

set -e

echo "================================================"
echo "Jules Assessment Remediator - Test Script"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}✗ GitHub CLI (gh) is not installed${NC}"
    echo "  Install from: https://cli.github.com/"
    exit 1
fi
echo -e "${GREEN}✓ GitHub CLI installed${NC}"

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}✗ Not authenticated with GitHub${NC}"
    echo "  Run: gh auth login"
    exit 1
fi
echo -e "${GREEN}✓ GitHub authenticated${NC}"

# Check if in git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}✗ Not in a git repository${NC}"
    exit 1
fi
echo -e "${GREEN}✓ In git repository${NC}"

# Check if workflow file exists
WORKFLOW_FILE=".github/workflows/Jules-Assessment-Remediator.yml"
if [ ! -f "$WORKFLOW_FILE" ]; then
    echo -e "${RED}✗ Workflow file not found: $WORKFLOW_FILE${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Workflow file exists${NC}"

echo ""
echo "================================================"
echo "Workflow Configuration Check"
echo "================================================"
echo ""

# Validate YAML syntax
echo "Validating YAML syntax..."
if command -v yamllint &> /dev/null; then
    if yamllint "$WORKFLOW_FILE" &> /dev/null; then
        echo -e "${GREEN}✓ YAML syntax valid${NC}"
    else
        echo -e "${YELLOW}⚠ YAML linting warnings (non-critical)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ yamllint not installed, skipping syntax check${NC}"
    echo "  Install with: pip install yamllint"
fi

# Check for required secrets
echo ""
echo "Checking required secrets..."
echo -e "${YELLOW}Note: Cannot verify secrets from CLI, please check manually:${NC}"
echo "  1. Go to: Settings > Secrets and variables > Actions"
echo "  2. Verify 'JULES_API_KEY' is set"
echo ""

# List assessment issues
echo "================================================"
echo "Assessment Issues Check"
echo "================================================"
echo ""

echo "Fetching assessment issues..."
ISSUE_COUNT=$(gh issue list --label "assessment" --state open --json number --jq '. | length')

if [ "$ISSUE_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}⚠ No open assessment issues found${NC}"
    echo "  The workflow will not have anything to remediate"
    echo "  Create test issues with label 'assessment' and 'priority: critical' or 'priority: high'"
else
    echo -e "${GREEN}✓ Found $ISSUE_COUNT open assessment issue(s)${NC}"
    echo ""
    echo "Issues:"
    gh issue list --label "assessment" --state open --json number,title,labels | \
        jq -r '.[] | "  #\(.number): \(.title) [\(.labels | map(.name) | join(", "))]"'
fi

echo ""
echo "================================================"
echo "Dry Run Test"
echo "================================================"
echo ""

read -p "Do you want to trigger a dry-run test? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Triggering dry-run workflow..."

    # Trigger workflow in dry-run mode
    gh workflow run Jules-Assessment-Remediator.yml \
        -f issue_count=3 \
        -f priority_filter=both \
        -f dry_run=true

    echo -e "${GREEN}✓ Workflow triggered in dry-run mode${NC}"
    echo ""
    echo "Monitor progress:"
    echo "  gh run list --workflow=Jules-Assessment-Remediator.yml --limit 1"
    echo ""
    echo "View logs:"
    echo "  gh run view --log"
    echo ""
    echo "Or visit: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/actions"
else
    echo "Dry-run skipped"
fi

echo ""
echo "================================================"
echo "Next Steps"
echo "================================================"
echo ""
echo "1. Review dry-run results in GitHub Actions"
echo "2. If successful, run in production mode:"
echo "   gh workflow run Jules-Assessment-Remediator.yml -f dry_run=false"
echo ""
echo "3. Monitor the created PR:"
echo "   - Verify automated fixes are correct"
echo "   - Check that tests pass"
echo "   - Review and merge"
echo ""
echo "4. For more information, see:"
echo "   docs/workflows/ASSESSMENT_REMEDIATION_GUIDE.md"
echo ""
echo "================================================"
echo "Test Complete"
echo "================================================"
