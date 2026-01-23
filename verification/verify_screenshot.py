from playwright.sync_api import sync_playwright
import os

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        cwd = os.getcwd()
        file_path = f"file://{cwd}/verification_repro.html"

        page.goto(file_path)
        page.wait_for_timeout(1000) # Wait for splash to appear

        screenshot_path = f"{cwd}/verification/splash_screen.png"
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        browser.close()

if __name__ == "__main__":
    run_verification()
