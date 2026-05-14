import sys

with open('repositories/repositories.qmd', 'r') as f:
    content = f.read()

content = content.replace('<span class="accordion-icon">+</span>', '<span class="accordion-icon" aria-hidden="true">+</span>')

with open('repositories/repositories.qmd', 'w') as f:
    f.write(content)
