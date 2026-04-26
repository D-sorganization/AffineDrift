with open(".github/workflows/ci-standard.yml", "r") as f:
    content = f.read()

# Replace if false with true if there is one for matlab-tests
content = content.replace("if: false  # Disabled due to corrupted MATLAB files", "")
content = content.replace("if: false", "") # Just in case

# We don't remove continue-on-error from MATLAB Quality Check because the issue says "where appropriate" and the python one has it, maybe we should remove it from the python one?
import re
content = re.sub(r'(\s+)- name: MATLAB Quality Check\n(\s+)continue-on-error: true', r'\1- name: MATLAB Quality Check', content)

with open(".github/workflows/ci-standard.yml", "w") as f:
    f.write(content)
