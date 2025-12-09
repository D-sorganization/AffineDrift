from playwright.sync_api import sync_playwright, Page
from pathlib import Path

def verify_layout(page: Page) -> None:
    """
    Verify the layout of the articles page by taking a screenshot and checking element heights.
    
    Args:
        page: The Playwright page object.
    """
    print("Navigating to articles.html...")
    # Use localhost:8080 as this is verification for local dev server
    page.goto("http://localhost:8080/articles.html")

    # Wait for the grid to be visible
    print("Waiting for .standard-page-layout...")
    page.wait_for_selector(".standard-page-layout")

    # Take screenshot
    print("Taking screenshot...")
    screenshot_path = Path(__file__).parent / "verification.png"
    page.screenshot(path=str(screenshot_path))

    # Check heights
    layout = page.locator(".standard-page-layout")
    layout_box = layout.bounding_box()
    left_box = page.locator(".left-sidebar").bounding_box()

    if layout_box and left_box:
        print(f"Layout Height: {layout_box['height']}")
        print(f"Sidebar Height: {left_box['height']}")
    else:
        print("Could not get bounding box.")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 800})
        verify_layout(page)
        browser.close()
