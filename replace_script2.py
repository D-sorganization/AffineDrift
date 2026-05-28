import re

with open('script.js', 'r') as f:
    content = f.read()

new_content = re.sub(
    r"      const focusableSelector =[\s\S]*?'button, \[href\], input, select, textarea, \[tabindex\]:not\(\[tabindex=\"-1\"\]\)';[\s\S]*?const focusableContent = lightbox\.querySelectorAll\(focusableSelector\);",
    r"      // ⚡ Bolt Optimization: Use getElementsByTagName('*') and filter manually instead of querySelectorAll\n      const focusableContent = [];\n      const allElements = lightbox.getElementsByTagName('*');\n      for (const el of allElements) {\n        if (el.tabIndex >= 0 && !el.disabled) {\n          focusableContent.push(el);\n        }\n      }",
    content
)

# Also let's check other usages of querySelectorAll inside loops or high frequency code paths.
