import os
import sys
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        file_path = os.path.abspath("verification_repro.html")
        page.goto(f"file://{file_path}")

        # Wait for splash
        page.wait_for_selector("#ad-splash-screen", state="visible")

        # Wait a bit for animation
        page.wait_for_timeout(500)

        # Take screenshot
        output_path = "/home/jules/verification/splash_screen.png"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        page.screenshot(path=output_path)
        print(f"Screenshot saved to {output_path}")

        browser.close()

if __name__ == "__main__":
    main()
