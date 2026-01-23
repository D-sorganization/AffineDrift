"""
Verification script for startup launcher fixes.
"""

import os
import time
from playwright.sync_api import sync_playwright, expect

def verify_startup():
    cwd = os.getcwd()
    url = f"file://{cwd}/tests/verification/verify_startup.html"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        logs = []
        def on_console(msg):
            logs.append(msg.text)
            print(f"Console: {msg.text}")

        page.on("console", on_console)

        print(f"Navigating to {url}")
        page.goto(url)

        # Wait for splash screen to appear (it should be immediate)
        splash = page.locator("#ad-splash-screen")
        expect(splash).to_be_visible(timeout=5000)
        print("Splash screen visible.")
        page.screenshot(path="tests/verification/splash_screen.png")

        # Wait for splash screen to disappear.
        # It gets the class 'ad-splash-hidden' and then is removed from DOM.
        # expect(splash).to_be_hidden() handles both cases.
        expect(splash).to_be_hidden(timeout=10000)
        print("Splash screen hidden.")

        # Check isReady state
        is_ready = page.evaluate("window.AffineDriftStartup.isReady()")
        print(f"isReady: {is_ready}")

        if not is_ready:
            print("FAILURE: window.AffineDriftStartup.isReady() returned false!")
            raise AssertionError("window.AffineDriftStartup.isReady() returned false")

        # Check logs for NaN or undefined in metrics
        for log in logs:
            if "NaNms" in log or "undefinedms" in log:
                 print(f"FAILURE: Found invalid metric log: {log}")
                 raise AssertionError(f"Invalid metric log found: {log}")

        print("Verification PASSED")
        browser.close()

if __name__ == "__main__":
    verify_startup()
