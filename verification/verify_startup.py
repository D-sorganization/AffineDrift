from playwright.sync_api import sync_playwright
import os

def verify_startup_visual():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Load the HTML file
        file_path = os.path.abspath("verification/verification_test.html")
        page.goto(f"file://{file_path}")

        # Wait for progress bar to appear
        page.wait_for_selector("#ad-splash-progress-bar")

        # Take screenshot of the splash screen
        page.screenshot(path="verification/startup_screenshot.png")
        print("Screenshot taken.")

        browser.close()

if __name__ == "__main__":
    verify_startup_visual()
