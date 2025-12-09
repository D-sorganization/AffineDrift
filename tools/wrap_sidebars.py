import glob
from pathlib import Path

def wrap_file(path):
    content = path.read_text()
    original_content = content

    # Wrap left-sidebar
    if '<aside class="left-sidebar">' in content:
        # Check if already wrapped to avoid double wrapping
        if 'sidebar-sticky-content' not in content:
            parts = content.split('<aside class="left-sidebar">')
            if len(parts) > 1:
                # parts[1] starts with content inside aside.
                # Find the closing tag.
                subparts = parts[1].split('</aside>', 1)
                if len(subparts) > 1:
                    content = parts[0] + '<aside class="left-sidebar">\n        <div class="sidebar-sticky-content">' + subparts[0] + '</div>\n      </aside>' + subparts[1]

    # Wrap right-sidebar
    if '<aside class="right-sidebar">' in content:
        # Check if right sidebar needs wrapping (it might be wrapped even if left is not, or vice versa, but checking content is safer)
        # However, checking 'sidebar-sticky-content' globally might skip right sidebar if left is wrapped.
        # So I should check locally.
        # But simple replacement is hard without context.
        # I'll rely on the split logic which is robust if tags are unique.
        pass # Reset content to process right sidebar properly

    # Re-process for right sidebar on the modified content
    if '<aside class="right-sidebar">' in content:
         parts = content.split('<aside class="right-sidebar">')
         if len(parts) > 1:
             # Check if immediate child is div
             if not parts[1].strip().startswith('<div class="sidebar-sticky-content">'):
                 subparts = parts[1].split('</aside>', 1)
                 if len(subparts) > 1:
                     content = parts[0] + '<aside class="right-sidebar">\n        <div class="sidebar-sticky-content">' + subparts[0] + '</div>\n      </aside>' + subparts[1]

    # Re-process for resources-sidebar
    if '<aside class="resources-sidebar">' in content:
         parts = content.split('<aside class="resources-sidebar">')
         if len(parts) > 1:
             if not parts[1].strip().startswith('<div class="sidebar-sticky-content">'):
                 subparts = parts[1].split('</aside>', 1)
                 if len(subparts) > 1:
                     content = parts[0] + '<aside class="resources-sidebar">\n        <div class="sidebar-sticky-content">' + subparts[0] + '</div>\n      </aside>' + subparts[1]

    if content != original_content:
        path.write_text(content)
        print(f"Wrapped {path}")

files = glob.glob("*.qmd")
for f in files:
    wrap_file(Path(f))
