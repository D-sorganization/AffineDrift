
import os
import sys
from playwright.sync_api import sync_playwright

def verify_layout():
    # Ensure docs directory exists and we can find the file
    docs_path = os.path.abspath("docs/articles.html")
    if not os.path.exists(docs_path):
        print(f"Error: {docs_path} does not exist. Please run build-html.py first or ensure docs are present.")
        return

    file_url = f"file://{docs_path}"
    print(f"Loading {file_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Desktop view
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(file_url)
        page.wait_for_load_state("networkidle")

        # Take screenshot of the top section where layout is visible
        page.screenshot(path="verification/layout_desktop_1920.png")
        print("Captured layout_desktop_1920.png")

        # Laptop view
        page.set_viewport_size({"width": 1366, "height": 768})
        page.screenshot(path="verification/layout_laptop_1366.png")
        print("Captured layout_laptop_1366.png")

        # Tablet view (potential trouble spot)
        page.set_viewport_size({"width": 1024, "height": 768})
        page.screenshot(path="verification/layout_tablet_1024.png")
        print("Captured layout_tablet_1024.png")

        # Mobile view
        page.set_viewport_size({"width": 375, "height": 812})
        page.screenshot(path="verification/layout_mobile_375.png")
        print("Captured layout_mobile_375.png")

        browser.close()

if __name__ == "__main__":
    verify_layout()
