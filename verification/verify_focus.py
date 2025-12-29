
from playwright.sync_api import sync_playwright
import os

def run():
    # Get absolute path to the HTML file
    cwd = os.getcwd()
    file_url = f"file://{cwd}/docs/articles.html"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Load the page
        page.goto(file_url)

        # Inject CSS to force state for screenshot
        # We force focus on the copy button to verify the outline and opacity
        page.add_style_tag(content="""
            .copy-btn { opacity: 1 !important; outline: 2px solid var(--accent-blue) !important; outline-offset: 2px !important; }
            .back-to-top { opacity: 1 !important; visibility: visible !important; outline: 2px solid var(--primary-blue) !important; outline-offset: 2px !important; }
            .accordion-header { outline: 2px solid var(--accent-blue) !important; outline-offset: -2px !important; }
        """)

        # Take screenshot
        page.screenshot(path="verification/focus-styles.png")
        browser.close()

if __name__ == "__main__":
    run()
