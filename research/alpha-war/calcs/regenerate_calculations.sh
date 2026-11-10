#!/usr/bin/env bash
# Regenerate Alpha War sensitivity JSON from a pinned UpstreamDrift checkout.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CALCS_DIR="${REPO_ROOT}/research/alpha-war/calcs"
LOCK_FILE="${CALCS_DIR}/upstream_drift.lock.json"

if ! command -v git >/dev/null 2>&1; then
  echo "error: git is required" >&2
  exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 is required" >&2
  exit 1
fi

PIN_COMMIT="$(python3 -c "import json; print(json.load(open('${LOCK_FILE}'))['commit'])")"
REPO_URL="$(python3 -c "import json; print(json.load(open('${LOCK_FILE}'))['repository'])")"

if [[ -z "${ALPHA_WAR_UPSTREAM_DRIFT_ROOT:-}" ]]; then
  echo "error: set ALPHA_WAR_UPSTREAM_DRIFT_ROOT to an UpstreamDrift clone at ${PIN_COMMIT:0:12}…" >&2
  echo "example:" >&2
  echo "  git clone \"${REPO_URL}\" /tmp/UpstreamDrift" >&2
  echo "  cd /tmp/UpstreamDrift && git checkout \"${PIN_COMMIT}\"" >&2
  echo "  export ALPHA_WAR_UPSTREAM_DRIFT_ROOT=/tmp/UpstreamDrift" >&2
  exit 1
fi

HEAD="$(git -C "${ALPHA_WAR_UPSTREAM_DRIFT_ROOT}" rev-parse HEAD)"
if [[ "${HEAD}" != "${PIN_COMMIT}" && "${HEAD}" != "${PIN_COMMIT:0:12}"* ]]; then
  echo "error: UpstreamDrift HEAD ${HEAD:0:12}… does not match lock ${PIN_COMMIT:0:12}…" >&2
  exit 1
fi

export ALPHA_WAR_UPSTREAM_DRIFT_ROOT
export ALPHA_WAR_INTEGRATION_REQUIRED=1
BACKUP_JSON="${CALCS_DIR}/.alpha_war_calculations.pre_regen.json"
cp "${CALCS_DIR}/alpha_war_calculations.json" "${BACKUP_JSON}"
python3 "${CALCS_DIR}/alpha_war_sensitivity_suite.py"
python3 -c "
from pathlib import Path
import sys
sys.path.insert(0, '${CALCS_DIR}')
from alpha_war_json_compare import compare_export_files
summary = compare_export_files(
    Path('${BACKUP_JSON}'),
    Path('${CALCS_DIR}/alpha_war_calculations.json'),
)
if summary.get('mismatch_count', 0):
    raise SystemExit(f'regenerated studies exceed tolerance: {summary}')
print('regeneration_compare', summary)
"
python3 -m unittest discover -s "${CALCS_DIR}" -p "test_alpha_war_*.py" -v
