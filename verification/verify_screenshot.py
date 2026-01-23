import os
import time
from playwright.sync_api import sync_playwright

def run():
    print("Starting visual verification...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Open the file
        file_path = os.path.abspath("verification/verification_test.html")
        url = f"file://{file_path}"
        print(f"Navigating to {url}")

        # We need to capture splash screen before it disappears.
        # But locally it might be too fast or too slow.
        # Startup launcher has MINIMUM_SPLASH_DURATION = 800ms.

        page.goto(url)

        # Take screenshot of splash
        # We can force it to stay if we want, or just snap quickly.
        # Or wait for it to be visible.
        try:
            page.wait_for_selector("#ad-splash-screen", state="visible", timeout=2000)
            page.screenshot(path="verification/splash_screen.png")
            print("Captured splash_screen.png")
        except:
            print("Could not capture splash screen (maybe too fast?)")

        # Wait for page reveal (splash hidden)
        try:
            # Wait for splash to have class 'ad-splash-hidden'
            page.wait_for_selector(".ad-splash-hidden", timeout=5000)
            # Or wait for it to be detached
            # page.wait_for_selector("#ad-splash-screen", state="detached", timeout=5000)

            # Wait a bit for reveal animation
            time.sleep(1)
            page.screenshot(path="verification/page_revealed.png")
            print("Captured page_revealed.png")
        except Exception as e:
            print(f"Error waiting for reveal: {e}")

        browser.close()

if __name__ == "__main__":
    run()
