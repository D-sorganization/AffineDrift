import os

from playwright.sync_api import sync_playwright


def run() -> None:
    """Run the Playwright test for accordion accessibility to verify state changes."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Load the test file
        file_path = os.path.abspath("test_accordion.html")
        page.goto(f"file://{file_path}")

        # Wait for script to run
        page.wait_for_load_state("domcontentloaded")

        # Check first accordion (collapsed initially)
        btn1 = page.locator(".accordion-header").nth(0)
        content1 = page.locator(".accordion-content").nth(0)

        # Verify aria-controls and id
        content1_id = content1.get_attribute("id")
        assert content1_id and content1_id.startswith("accordion-content-"), f"ID not generated: {content1_id}"
        assert btn1.get_attribute("aria-controls") == content1_id, "aria-controls mismatch"

        # Verify initial aria-hidden (should be true because expanded=false)
        assert content1.get_attribute("aria-hidden") == "true", "aria-hidden should be true for collapsed"

        # Click to expand
        btn1.click()

        # Verify expanded state
        assert btn1.get_attribute("aria-expanded") == "true", "Should be expanded"
        assert content1.get_attribute("aria-hidden") == "false", "aria-hidden should be false for expanded"

        # Check second accordion (expanded initially)
        btn2 = page.locator(".accordion-header").nth(1)
        content2 = page.locator(".accordion-content").nth(1)

        # Verify initial aria-hidden (should be false because expanded=true)
        assert content2.get_attribute("aria-hidden") == "false", "aria-hidden should be false for initially expanded"

        # Click to collapse
        btn2.click()

        assert btn2.get_attribute("aria-expanded") == "false", "Should be collapsed"
        assert content2.get_attribute("aria-hidden") == "true", "aria-hidden should be true for collapsed"

        print("✅ Accordion accessibility verification passed!")
        browser.close()

if __name__ == "__main__":
    run()
