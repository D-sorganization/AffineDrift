import os
import sys
import time
from playwright.sync_api import sync_playwright

def verify_screenshot():
    cwd = os.getcwd()
    file_path = f"file://{cwd}/verification/verification_startup.html"
    screenshot_path = "verification/splash_screen.png"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        print(f"Navigating to {file_path}")
        page.goto(file_path)

        # Wait for splash screen
        splash = page.locator("#ad-splash-screen")
        splash.wait_for(state="visible", timeout=5000)

        # Wait for logo or title
        print("Waiting for content...")
        page.locator(".ad-splash-title").wait_for(state="visible", timeout=5000)

        # Wait a bit for animations to progress
        time.sleep(1)

        # Take screenshot
        print(f"Taking screenshot to {screenshot_path}")
        page.screenshot(path=screenshot_path)

        browser.close()

if __name__ == "__main__":
    verify_screenshot()
