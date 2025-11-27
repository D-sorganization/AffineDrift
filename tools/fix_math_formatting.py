#!/usr/bin/env python3
"""
Fix math formatting in Quarto files
Converts **X** to \\mathbf{X} in math contexts
"""

import re
import sys


def fix_math_formatting(content):
    """Fix math formatting issues"""

    # Pattern to match **X** in math mode (between $ or $$)
    # We need to be careful to only replace in math contexts

    # Replace **X** with \mathbf{X} in inline math ($...$)
    def replace_inline_math(match):
        math_content = match.group(1)
        # Replace **X** with \mathbf{X} (single letter)
        math_content = re.sub(r'\*\*([A-Za-z])\*\*', r'\\mathbf{\1}', math_content)
        # Replace **\alpha** etc with \boldsymbol{\alpha}
        math_content = re.sub(r'\*\*\\([a-z]+)\*\*', r'\\boldsymbol{\\\1}', math_content)
        return f'${math_content}$'

    # Use non-greedy matching to handle multiple inline math expressions
    content = re.sub(r'\$([^$]+?)\$', replace_inline_math, content)

    # Replace **X** with \mathbf{X} in display math ($$...$$)
    def replace_display_math(match):
        math_content = match.group(1)
        # Replace **X** with \mathbf{X}
        math_content = re.sub(r'\*\*([A-Za-z])\*\*', r'\\mathbf{\1}', math_content)
        # Also handle Greek letters: **\alpha** -> \boldsymbol{\alpha}
        math_content = re.sub(r'\*\*\\([a-z]+)\*\*', r'\\boldsymbol{\\\1}', math_content)
        return f'$${math_content}$$'

    content = re.sub(r'\$\$([^$]+)\$\$', replace_display_math, content, flags=re.DOTALL)

    return content

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python fix_math_formatting.py <file.qmd>")
        sys.exit(1)

    filepath = sys.argv[1]

    with open(filepath, encoding='utf-8') as f:
        content = f.read()

    content = fix_math_formatting(content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Fixed math formatting in {filepath}")

