from playwright.sync_api import sync_playwright

def verify_layout(page):
    print("Navigating to articles.html...")
    page.goto("http://localhost:8080/articles.html")

    # Wait for the grid to be visible
    print("Waiting for .standard-page-layout...")
    page.wait_for_selector(".standard-page-layout")

    # Take screenshot
    print("Taking screenshot...")
    page.screenshot(path="/home/jules/verification/verification.png")

    # Check heights
    layout = page.locator(".standard-page-layout")
    layout_box = layout.bounding_box()
    left_box = page.locator(".left-sidebar").bounding_box()

    print(f"Layout Height: {layout_box['height']}")
    print(f"Sidebar Height: {left_box['height']}")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 800})
        verify_layout(page)
        browser.close()
