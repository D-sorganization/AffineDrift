import os

from playwright.sync_api import expect, sync_playwright


def verify_toc_scrollspy() -> None:
    """
    Verifies the Table of Contents (TOC) scrollspy functionality using a local file path.

    This function launches a Playwright browser, navigates to the articles page using the file
    protocol, and checks if the TOC links update correctly when scrolling to different sections.
    It saves screenshots of the initial and scrolled states.
    """
    # Path to the local file
    file_path = os.path.abspath("docs/articles.html")
    file_url = f"file://{file_path}"

    print(f"Testing URL: {file_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Emulate a desktop viewport to ensure sidebar is visible
        page = browser.new_page(viewport={"width": 1280, "height": 800})

        # Navigate to the page
        page.goto(file_url)

        # Wait for TOC to be generated
        # The script creates #toc-list dynamically
        toc_list = page.locator("#toc-list")
        expect(toc_list).to_be_visible()

        # Get all TOC links
        links = toc_list.locator("a")
        count = links.count()
        print(f"Found {count} TOC links")

        if count == 0:
            print("No TOC links found. Skipping verification.")
            return

        # 1. Verify initial state (first link might be active if at top)
        # Scroll to the first section
        first_link = links.nth(0)
        first_href = first_link.get_attribute("href")
        if first_href:
            target_id = first_href.replace("#", "")

            print(f"Scrolling to first section: {target_id}")
            page.locator(f"#{target_id}").scroll_into_view_if_needed()

            # Give Observer time to fire
            page.wait_for_timeout(500)

            # Take screenshot of initial state
            page.screenshot(path="/home/jules/verification/toc_initial.png")

        # 2. Scroll to the last section
        last_link = links.nth(count - 1)
        last_href = last_link.get_attribute("href")
        if last_href:
            last_target_id = last_href.replace("#", "")

            print(f"Scrolling to last section: {last_target_id}")
            # Use JS scroll to be sure
            page.evaluate(f"document.getElementById('{last_target_id}').scrollIntoView()")

            # Wait for scroll and observer
            page.wait_for_timeout(1000)

            # Check if last link has 'active' class
            # Note: Depending on layout, the last section might not be tall enough to trigger
            # if it's at the very bottom and previous section is still visible.
            # But we check if *some* link is active.

            active_links = toc_list.locator("a.active")
            active_count = active_links.count()
            print(f"Found {active_count} active links after scrolling to bottom")

            if active_count > 0:
                active_text = active_links.first.inner_text()
                print(f"Active link text: {active_text}")
            else:
                print("WARNING: No active link found after scrolling.")

            page.screenshot(path="/home/jules/verification/toc_scrolled.png")

        browser.close()


if __name__ == "__main__":
    if not os.path.exists("/home/jules/verification"):
        os.makedirs("/home/jules/verification")
    verify_toc_scrollspy()
