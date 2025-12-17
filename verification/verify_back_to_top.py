from playwright.sync_api import sync_playwright


def verify_back_to_top() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})

        # Navigate to index
        page.goto("http://localhost:8000/index.html")

        # Force body height to ensure scrolling
        page.evaluate("document.body.style.minHeight = '5000px'")

        # Initial state: button should be hidden
        _btn = page.locator(".back-to-top")

        # Scroll down to make it visible (> 300px)
        page.evaluate("window.scrollTo(0, 500)")
        page.wait_for_timeout(1000)  # Wait for transition

        # Take a screenshot of the button area (bottom right)
        # Button is at bottom: 2rem, right: 2rem.
        # 2rem = 36px (18px base). So ~72px from edges?
        # Button size 3rem = 54px.
        page.screenshot(path="verification/back_to_top_start.png")

        # Scroll to middle
        page.evaluate("window.scrollTo(0, 2500)")
        page.wait_for_timeout(500)
        page.screenshot(path="verification/back_to_top_middle.png")

        # Scroll to near bottom
        page.evaluate("window.scrollTo(0, 5000)")
        page.wait_for_timeout(500)
        page.screenshot(path="verification/back_to_top_end.png")

        browser.close()


if __name__ == "__main__":
    verify_back_to_top()
