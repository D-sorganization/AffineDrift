from playwright.sync_api import sync_playwright, expect
import os
import time

def verify_startup():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Get absolute path to the HTML file
        html_path = os.path.abspath("tests/verification/verify_startup.html")
        page.goto(f"file://{html_path}")

        # 1. Verify Splash Screen is present and visible initially
        splash = page.locator("#ad-splash-screen")
        expect(splash).to_be_visible()
        print("Splash screen is visible.")

        # Take a screenshot of the splash screen
        page.screenshot(path="tests/verification/splash_visible.png")

        # 2. Verify progress bar exists
        progress = page.locator("#ad-splash-progress-bar")
        expect(progress).to_be_attached()
        print("Progress bar is attached.")

        # 3. Wait for splash to be hidden (it happens after load + min duration)
        # We need to wait a bit. The script has a MINIMUM_SPLASH_DURATION of 800ms.
        # And it waits for DOMContentLoaded + window load.
        # Since this is a local file, load should be fast.

        # Wait for the splash to have the 'ad-splash-hidden' class
        # Note: expect(...).to_have_class can handle classes list
        # using a regex to match the class presence
        import re
        expect(splash).to_have_class(re.compile(r"ad-splash-hidden"), timeout=10000)
        print("Splash screen is hidden.")

        # 4. Verify content is revealed
        # The body should have 'ad-page-revealed' class on documentElement?
        # The script does: document.documentElement.classList.add('ad-page-revealed');
        # Wait, check root element.
        root = page.locator("html")
        expect(root).to_have_class(re.compile(r"ad-page-revealed"))
        print("Page is revealed.")

        # Take a screenshot of the revealed page
        page.screenshot(path="tests/verification/page_revealed.png")

        # 5. Verify API
        is_ready = page.evaluate("window.AffineDriftStartup.isReady()")
        print(f"isReady state: {is_ready}")
        if is_ready is not True:
             print("Error: isReady should be true")
             exit(1)

        print("Verification successful!")
        browser.close()

if __name__ == "__main__":
    verify_startup()
