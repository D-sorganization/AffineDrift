import os
from playwright.sync_api import sync_playwright

def verify_startup():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Absolute path to the html file
        file_path = os.path.abspath("verification/test_startup.html")
        page.goto(f"file://{file_path}")

        # Wait for splash screen
        page.wait_for_selector("#ad-splash-screen", state="attached")
        print("Splash screen found")

        # Wait for isReady
        page.wait_for_function("() => window.AffineDriftStartup && window.AffineDriftStartup.isReady()")
        print("isReady is true")

        # Take screenshot of the "revealed" state (which is what isReady implies, or close to it)
        # Note: when isReady becomes true, the splash might be hidden or animating out.
        # Let's wait a bit to see the content?
        # Actually, the splash fades out.
        # Let's verify the splash screen appearance FIRST before it disappears?
        # But it disappears fast (minimum 800ms).
        # We can take a screenshot immediately after load.

        page.reload()
        # Verify splash visible
        page.wait_for_selector("#ad-splash-screen")
        page.screenshot(path="verification/splash_screen.png")
        print("Screenshot taken")

        browser.close()

if __name__ == "__main__":
    verify_startup()
