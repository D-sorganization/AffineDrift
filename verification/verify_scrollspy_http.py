import os

from playwright.sync_api import expect, sync_playwright


def verify_toc_scrollspy_http():
    # Use HTTP server
    url = "http://localhost:8000/articles.html"

    print(f"Testing URL: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})

        page.goto(url)

        # Wait for TOC
        toc_list = page.locator("#toc-list")
        expect(toc_list).to_be_visible()

        links = toc_list.locator("a")
        count = links.count()
        print(f"Found {count} TOC links")

        # Scroll to a middle section to ensure intersection
        # The articles.html page might be short or have specific layout.
        # Let's try to scroll to the second section if available.

        if count >= 2:
            target_link = links.nth(1)
            target_href = target_link.get_attribute("href")
            target_id = target_href.replace("#", "")
            print(f"Scrolling to section: {target_id}")

            # Scroll element into view
            page.locator(f"#{target_id}").scroll_into_view_if_needed()

            # Additional scroll to center it
            page.evaluate(
                f"document.getElementById('{target_id}').scrollIntoView({{block: 'center'}})"
            )

            page.wait_for_timeout(1000)

            # Check if class is added
            is_active = target_link.get_attribute("class")
            print(f"Link class: {is_active}")

            # Take screenshot
            page.screenshot(path="/home/jules/verification/toc_active.png")

        browser.close()


if __name__ == "__main__":
    if not os.path.exists("/home/jules/verification"):
        os.makedirs("/home/jules/verification")
    verify_toc_scrollspy_http()
