#!/usr/bin/env python3
"""
Update navigation across all HTML pages
"""
import os
import re

# New navigation structure
NEW_NAV = '''                <ul class="nav-links">
                    <li><a href="index.html">Affine Drift</a></li>
                    <li><a href="articles.html">Articles</a></li>
                    <li><a href="research-reviews.html">Reviews</a></li>
                    <li><a href="resources.html">Resources</a></li>
                    <li><a href="book-reviews.html">Book Reviews</a></li>
                    <li><a href="daydreams-doodles.html">Daydreams & Doodles</a></li>
                    <li><a href="contact.html">Contact</a></li>
                    <li><a href="about.html">About</a></li>
                </ul>'''

# Pages that need updating
PAGES_TO_UPDATE = [
    'book-reviews.html',
    'contact.html',
    'daydreams-doodles.html',
    'modelling.html',
    'research-reviews.html',
    'theory-part1.html',
    'theory-part2.html',
    'theory-part3.html',
    'theory-part4.html',
    'theory-part5.html',
    'theory.html',
    'wscg-research.html'
]

def update_navigation(filepath):
    """Update navigation in a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match the nav-links ul
    pattern = r'<ul class="nav-links">.*?</ul>'

    # Replace with new navigation
    updated_content = re.sub(pattern, NEW_NAV, content, flags=re.DOTALL)

    # Also update nav tag to nav class="top-nav"
    updated_content = updated_content.replace('<nav>', '<nav class="top-nav">')

    # Also update logo path if needed
    updated_content = updated_content.replace('logo/AffineDriftLogo.png', 'logo/Logo Transparent/1.png')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print(f"✓ Updated {filepath}")

def main():
    for page in PAGES_TO_UPDATE:
        if os.path.exists(page):
            update_navigation(page)
        else:
            print(f"✗ Not found: {page}")

if __name__ == '__main__':
    main()
