from playwright.sync_api import sync_playwright, expect
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load the mock HTML file
        cwd = os.getcwd()
        url = f"file://{cwd}/verification/mock_article.html"
        print(f"Navigating to {url}")
        page.goto(url)

        # Check title visibility
        header = page.locator(".critics-comments-header h2")
        expect(header).to_be_visible()
        expect(header).to_have_text("Critics' Comments")
        print("Header verified.")

        # Check that the new critique title exists in DOM
        new_critique_title = page.get_by_role("heading", name="Sensitivity to Measurement Noise")

        # Click the header to expand
        print("Clicking header to expand...")
        page.locator(".critics-comments-header").click()

        # Wait for potential CSS transition
        page.wait_for_timeout(1000)

        # Now check visibility
        print("Checking visibility of new critique...")
        if new_critique_title.is_visible():
            print("New critique IS visible.")
        else:
            print("New critique is NOT visible. Toggle failed?")

        expect(new_critique_title).to_be_visible()

        # Take screenshot
        output_path = "verification/critics_verification.png"
        page.screenshot(path=output_path, full_page=True)
        print(f"Screenshot saved to {output_path}")

        browser.close()

if __name__ == "__main__":
    run()
