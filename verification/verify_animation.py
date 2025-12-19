import sys
import time

from playwright.sync_api import Page, sync_playwright


def verify_animation(page: Page) -> None:  # type: ignore[no-any-unimported]
    """Verify animation logic by checking section opacity after scroll."""
    print("Navigating to home page...")
    page.goto("http://localhost:8000/index.html")
    page.wait_for_load_state("networkidle")

    # Find a section that is likely below the fold.
    # The home page usually has multiple sections.
    # We can get all sections and pick the last one.
    sections = page.locator("section:not(.page-header):not(.article-section)")
    count = sections.count()
    print(f"Found {count} sections.")

    if count == 0:
        print("No sections found to verify animation.")
        return

    last_section = sections.last

    # Scroll to the bottom to ensure it comes into view
    print("Scrolling to bottom...")
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    # Wait for animation (transition is 0.4s)
    time.sleep(1)

    # Check opacity
    opacity = last_section.evaluate("el => getComputedStyle(el).opacity")
    print(f"Opacity of last section: {opacity}")

    page.screenshot(path="verification/animation_verification.png")

    if opacity == "1":
        print("SUCCESS: Section is visible.")
    else:
        print(f"FAILURE: Section opacity is {opacity}, expected 1.")
        sys.exit(1)


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            verify_animation(page)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
        finally:
            browser.close()
