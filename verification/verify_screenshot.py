import os
from playwright.sync_api import sync_playwright

def verify_screenshot():
    html_path = os.path.abspath("verification/verification_test.html")
    url = f"file://{html_path}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Go to page
        page.goto(url)

        # Splash screen should be visible immediately
        # Wait for element to be attached to ensure we catch it
        splash = page.wait_for_selector("#ad-splash-screen")

        # Take screenshot of splash
        page.screenshot(path="verification/splash_screen.png")
        print("Screenshot saved to verification/splash_screen.png")

        browser.close()

if __name__ == "__main__":
    verify_screenshot()
