import os

from playwright.sync_api import sync_playwright


def test_splash(page):
    cwd = os.getcwd()
    file_path = os.path.join(cwd, "test_startup.html")
    url = f"file://{file_path}"
    print(f"Navigating to {url}")

    page.goto(url)

    # Wait for splash screen
    splash = page.locator("#ad-splash-screen")
    splash.wait_for(state="visible", timeout=2000)

    # Take screenshot of splash
    page.screenshot(path="verification/splash_screen.png")
    print("Splash screenshot taken.")

    # Verify progress bar exists
    progress = page.locator("#ad-splash-progress-bar")
    if progress.count() > 0:
        print("Progress bar found.")
    else:
        print("Progress bar NOT found.")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            test_splash(page)
        finally:
            browser.close()
