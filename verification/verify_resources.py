import os

from playwright.sync_api import sync_playwright


def run() -> None:
    """Run verification of the mock article using Playwright."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Determine absolute path
        cwd = os.getcwd()
        file_path = f"file://{cwd}/verification/mock_article.html"

        print(f"Navigating to: {file_path}")
        page.goto(file_path)

        # Wait for iframes (optional, just to see if they render layout)
        page.wait_for_timeout(2000)

        # Screenshot
        output_path = f"{cwd}/verification/verification.png"
        page.screenshot(path=output_path, full_page=True)
        print(f"Screenshot saved to: {output_path}")

        browser.close()


if __name__ == "__main__":
    run()
