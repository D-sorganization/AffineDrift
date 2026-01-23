import os
import time
from playwright.sync_api import sync_playwright

def verify_visual():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        filepath = os.path.abspath("verification/test_startup_visual.html")
        page.goto(f"file://{filepath}")

        # Wait for splash screen to be in DOM
        page.wait_for_selector("#ad-splash-screen")

        # Take screenshot of splash screen
        page.screenshot(path="verification/splash_screen.png")
        print("Screenshot taken: verification/splash_screen.png")

        browser.close()

if __name__ == "__main__":
    verify_visual()
