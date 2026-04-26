with open(".github/workflows/ci-standard.yml", "r") as f:
    content = f.read()

import re

# 2. Re-enable the `matlab-tests` job in `.github/workflows/ci-standard.yml`.
content = content.replace("  # matlab-tests:\n  #   needs: [pick-runner, quality-gate]\n  #   runs-on: self-hosted\n  #   steps:\n  #     - uses: actions/checkout@v4\n  #     - uses: matlab-actions/setup-matlab@v2\n  #     - uses: matlab-actions/run-command@v2\n  #       with:\n  #         command: |\n  #           addpath('matlab');\n  #           run_all",
"  matlab-tests:\n    needs: [pick-runner, quality-gate]\n    runs-on: d-sorg-fleet\n    steps:\n      - uses: actions/checkout@v4\n      - uses: matlab-actions/setup-matlab@v2\n      - uses: matlab-actions/run-command@v2\n        with:\n          command: |\n            addpath('matlab');\n            run_all")

# 3. Remove `continue-on-error: true` from critical quality checks where appropriate.
content = re.sub(r'(\s+)- name: MATLAB Quality Check\n(\s+)continue-on-error: true', r'\1- name: MATLAB Quality Check', content)

with open(".github/workflows/ci-standard.yml", "w") as f:
    f.write(content)
