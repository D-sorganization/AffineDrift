import re

file_path = 'content/wrist-as-universal-joint/Wrist_Universal_Claude.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix <p>...<ul> and <p>...<ol>
# We want to close the <p> tag before the list starts
content = re.sub(r'(<p>\s*where:)\s*(<ul>)', r'\1\n</p>\n\2', content)
content = re.sub(r'(<p>\s*The presence of.*?interaction of:)\s*(<ol>)', r'\1\n</p>\n\2', content, flags=re.DOTALL)
content = re.sub(r'(<p>\s*The radiocarpal.*?primary degrees of freedom:)\s*(<ul>)', r'\1\n</p>\n\2', content, flags=re.DOTALL)
content = re.sub(r'(<p>\s*\\paragraph\{Wrist coordinate system:\})\s*(<ul>)', r'\1\n</p>\n\2', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
