from pathlib import Path

from playwright.sync_api import sync_playwright


def run() -> None:
    """Run verification using Playwright."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Determine absolute path
        cwd = Path.cwd()
        file_path = f"file://{cwd}/verification/mock_article.html"

        page.goto(file_path)

        # Wait for iframes (optional, just to see if they render layout)
        page.wait_for_timeout(2000)

        # Screenshot
        output_path = cwd / "verification/verification.png"
        page.screenshot(path=str(output_path), full_page=True)

        browser.close()


if __name__ == "__main__":
    run()
