import os
import time
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720})

        # Get absolute path to the HTML file
        html_path = os.path.abspath("verification/test_startup.html")
        url = f"file://{html_path}"

        print(f"Loading {url}...")
        page.goto(url)

        # 1. Wait for splash screen
        print("Waiting for splash screen...")
        splash = page.locator("#ad-splash-screen")
        splash.wait_for(state="visible", timeout=5000)

        # 2. Take screenshot of splash screen
        print("Taking screenshot of splash screen...")
        # Wait a bit for animation to start
        time.sleep(0.5)
        page.screenshot(path="verification/startup_screenshot.png")
        print("Screenshot saved to verification/startup_screenshot.png")

        # 3. Wait for startup completion
        print("Waiting for startup sequence to complete...")
        splash.wait_for(state="hidden", timeout=10000)

        # 4. Verify isReady
        is_ready = page.evaluate("window.AffineDriftStartup && window.AffineDriftStartup.isReady()")
        if is_ready:
            print("PASS: window.AffineDriftStartup.isReady() returned true.")
        else:
            print("FAIL: window.AffineDriftStartup.isReady() returned false.")

        browser.close()

if __name__ == "__main__":
    run()
