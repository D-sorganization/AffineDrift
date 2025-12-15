from playwright.sync_api import sync_playwright, expect
import time

def verify_bibliography():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            # Navigate to the bibliography page
            page.goto("http://localhost:8000/bibliography.html")

            # Wait for the list to load (it's fetched via JS)
            # Expect at least one item
            bib_item = page.locator(".bib-item").first
            expect(bib_item).to_be_visible(timeout=5000)

            # Check for specific content
            expect(page.get_by_text("Sequential motions of body segments")).to_be_visible()

            # Take initial screenshot
            page.screenshot(path="verification/bibliography_initial.png")

            # Test search
            search_input = page.locator("#bib-search")
            search_input.fill("Zajac")

            # Verify filter works (Zajac should be visible)
            expect(page.get_by_text("Muscle coordination of movement")).to_be_visible()

            # Screenshot of filtered state
            page.screenshot(path="verification/bibliography_search.png", full_page=True)
            print("Screenshot saved to verification/bibliography_search.png")

            # Clear search and click an item
            search_input.fill("")
            # Wait for list to repopulate
            time.sleep(0.5)
            page.locator(".bib-item").first.click()

            # Verify details sidebar
            expect(page.locator("#bib-details")).to_contain_text("Reference Details")

            # Screenshot of details
            page.screenshot(path="verification/bibliography_details.png")
            print("Screenshot saved to verification/bibliography_details.png")

        except Exception as e:
            print(f"Error: {e}")
            # Take screenshot on error
            page.screenshot(path="verification/error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_bibliography()
