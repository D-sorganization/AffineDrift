import os
from playwright.sync_api import sync_playwright

def verify_startup():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Load the local HTML file
        file_path = os.path.abspath("verification/test_startup.html")
        page.goto(f"file://{file_path}")

        # Wait for splash screen to appear
        splash = page.locator("#ad-splash-screen")
        splash.wait_for(state="visible", timeout=5000)

        # Take a screenshot of the splash screen
        print("Taking screenshot of splash screen...")
        page.screenshot(path="verification/splash_screen.png")

        # Wait for isReady
        print("Waiting for startup to complete...")
        page.wait_for_function("window.AffineDriftStartup && window.AffineDriftStartup.isReady() === true", timeout=10000)

        # Take a screenshot of the revealed page
        print("Taking screenshot of revealed page...")
        page.screenshot(path="verification/revealed_page.png")

        browser.close()

if __name__ == "__main__":
    verify_startup()
