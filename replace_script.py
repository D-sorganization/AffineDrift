import re

with open('script.js', 'r') as f:
    content = f.read()

new_content = re.sub(
    r"const focusableSelector =[\s\S]*?'button, \[href\], input, select, textarea, \[tabindex\]:not\(\[tabindex=\"-1\"\]\)';[\s\S]*?const focusableContent = lightbox\.querySelectorAll\(focusableSelector\);",
    r"// ⚡ Bolt Optimization: Replace querySelectorAll with getElementsByTagName for focusable elements\n      const allElements = lightbox.getElementsByTagName('*');\n      const focusableContent = [];\n      for (const el of allElements) {\n        const tag = el.tagName;\n        if (tag === 'BUTTON' || tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') {\n            if (!el.disabled && el.tabIndex >= 0) focusableContent.push(el);\n        } else if (tag === 'A' && el.hasAttribute('href')) {\n            if (el.tabIndex >= 0) focusableContent.push(el);\n        } else if (el.hasAttribute('tabindex') && el.getAttribute('tabindex') !== '-1') {\n            focusableContent.push(el);\n        }\n      }",
    content
)

with open('script.js', 'w') as f:
    f.write(new_content)
