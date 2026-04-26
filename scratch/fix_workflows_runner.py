import os
import re

workflow_dir = '.github/workflows'
for filename in os.listdir(workflow_dir):
    if filename.endswith('.yml') or filename.endswith('.yaml'):
        path = os.path.join(workflow_dir, filename)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace banned tokens
        new_content = content.replace('runs-on: ubuntu-latest', 'runs-on: d-sorg-fleet')
        new_content = new_content.replace('runs-on: windows-latest', 'runs-on: d-sorg-fleet')
        new_content = new_content.replace('runs-on: macos-latest', 'runs-on: d-sorg-fleet')
        new_content = new_content.replace('runs-on: self-hosted', 'runs-on: d-sorg-fleet')
        
        # Hardened pick-runner
        # Match the old pick-runner pattern
        pick_runner_pattern = r'ONLINE=\$\(gh api /orgs/\$\{\{ github\.repository_owner \}\}/actions/runners .*?2>/dev/null \|\| echo \"0\"\)'
        
        hardened_replacement = r'ONLINE=$(gh api /orgs/${{ github.repository_owner }}/actions/runners --paginate \
              --jq \'if .runners then [.runners[] | select(.status == "online") | select(.labels[].name == "d-sorg-fleet")] | length else 0 end\' \
              2>/dev/null || echo "0")'
        
        new_content = re.sub(pick_runner_pattern, hardened_replacement, new_content, flags=re.DOTALL)
        
        if new_content != content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f'Fixed {filename}')
