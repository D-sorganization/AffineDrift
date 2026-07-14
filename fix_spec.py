import re

with open('SPEC.md', 'r') as f:
    content = f.read()

# Extract versions from changelog table
pattern = r"\|\s*\d{4}-\d{2}-\d{2}\s*\|\s*(\d+\.\d+\.\d+)\s*\|"
matches = re.findall(pattern, content)

def version_to_tuple(v):
    return tuple(map(int, v.split('.')))

if matches:
    max_version = max(matches, key=version_to_tuple)
    print(f"Latest version in SPEC.md: {max_version}")
else:
    print("No matches")
