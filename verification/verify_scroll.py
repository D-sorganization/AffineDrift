
from playwright.sync_api import Page, expect, sync_playwright
import time

def test_scroll_features(page: Page):
    # 1. Arrange: Go to the homepage.
    page.goto("http://localhost:8000/index.html")

    # Wait for the page to load and script to initialize
    page.wait_for_load_state("domcontentloaded")
    time.sleep(1) # Give a moment for JS to run init

    # 2. Act: Scroll down to trigger "Back to Top"
    # Threshold is 300px. We scroll to 500px.
    page.evaluate("window.scrollTo(0, 500)")

    # Wait for scroll event and rAF to process (debounced/throttled)
    time.sleep(0.5)

    # 3. Assert: Back to top button should be visible
    back_to_top = page.locator(".back-to-top")
    expect(back_to_top).to_have_class(re.compile(r"visible"))

    # Take screenshot of visible button
    page.screenshot(path="verification/scroll_down.png")
    print("Screenshot taken: scroll_down.png")

    # 4. Act: Scroll back up
    page.evaluate("window.scrollTo(0, 0)")
    time.sleep(0.5)

    # 5. Assert: Back to top button should be hidden (class removed)
    expect(back_to_top).not_to_have_class(re.compile(r"visible"))

    # Take screenshot of hidden button (optional, but good for verification)
    page.screenshot(path="verification/scroll_up.png")
    print("Screenshot taken: scroll_up.png")

import re

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            test_scroll_features(page)
            print("Verification successful!")
        except Exception as e:
            print(f"Verification failed: {e}")
            # Take screenshot on failure
            page.screenshot(path="verification/failure.png")
        finally:
            browser.close()
