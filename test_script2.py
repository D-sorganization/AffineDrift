import re

with open('js/accessibility.js', 'r') as f:
    content = f.read()

new_content = re.sub(
    r"const modals = document\.querySelectorAll\('\[role=\"dialog\"\]'\);",
    r"// ⚡ Bolt Optimization: Replace querySelectorAll with getElementsByTagName for modals\n    const allDialogs = document.getElementsByTagName('*');\n    const modals = [];\n    for (const el of allDialogs) {\n        if (el.getAttribute('role') === 'dialog') {\n            modals.push(el);\n        }\n    }",
    content
)

with open('js/accessibility.js', 'w') as f:
    f.write(new_content)
