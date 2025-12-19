import time

from playwright.sync_api import Page, sync_playwright


def verify_scroll(page: Page) -> None:
    """Verify that the scroll-to-top button appears after scrolling."""
    print("Navigating to home page...")
    page.goto("http://localhost:8000/index.html")

    # Wait for DOM to be ready
    page.wait_for_load_state("networkidle")

    # Check initial state (button should be hidden)
    back_to_top = page.locator(".back-to-top")

    # Scroll down > 300px
    print("Scrolling down...")
    page.evaluate("window.scrollTo(0, 500)")

    # Wait for rAF and transition (a bit longer since we are using rAF now)
    time.sleep(1)

    # Check if visible
    classes = back_to_top.get_attribute("class")
    print(f"Classes after scroll: {classes}")

    page.screenshot(path="verification/scroll_verification.png")

    if classes and "visible" in classes:
        print("SUCCESS: Back to top button is visible.")
    else:
        print("FAILURE: Back to top button is NOT visible.")
        exit(1)


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            verify_scroll(page)
        except Exception as e:
            print(f"Error: {e}")
            exit(1)
        finally:
            browser.close()
