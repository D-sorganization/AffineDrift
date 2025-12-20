from playwright.sync_api import sync_playwright
import os

def run():
    # Ensure verification directory exists
    os.makedirs("verification", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to a page with TOC
        url = "http://localhost:8000/articles/theory-part1.html"
        print(f"Navigating to {url}")

        response = page.goto(url)
        if not response.ok:
            print(f"Failed to load page: {response.status}")
            return

        # Wait for TOC to generate
        try:
            page.wait_for_selector("#toc-list", timeout=5000)
        except:
            print("TOC list not found")
            page.screenshot(path="verification/toc_error.png")
            return

        # Get the second link in TOC to scroll to
        toc_links = page.locator("#toc-list a")
        count = toc_links.count()
        print(f"Found {count} TOC links")

        if count > 1:
            # We skip the first one because it's usually the main title or intro which is active by default
            index_to_test = 2 if count > 2 else 1
            test_link = toc_links.nth(index_to_test)
            target_id_ref = test_link.get_attribute("href")

            if target_id_ref and target_id_ref.startswith("#"):
                target_id = target_id_ref.replace("#", "")
                print(f"Testing scroll to section: {target_id}")

                # Scroll the element into view (start)
                # We align it to the top to ensure it crosses the top threshold
                page.evaluate(f"const el = document.getElementById('{target_id}'); if(el) el.scrollIntoView({{behavior: 'instant', block: 'start'}});")

                # Adjust slightly to ensure it's not hidden behind fixed header if any (120px header)
                # But our IntersectionObserver handles the header offset via rootMargin.
                # If we scroll to 'start', it is at y=0.
                # rootMargin -100px means active zone is y>100.
                # So if element is at 0, it overlaps 0-Height.
                # Active zone is 100-Bottom.
                # They overlap. It should be active.

                # Wait for observer
                page.wait_for_timeout(1000)

                # Check classes
                classes = test_link.get_attribute("class") or ""
                print(f"Classes for link: '{classes}'")

                if "active" in classes.split():
                    print("SUCCESS: Link is active")
                else:
                    print("FAILURE: Link is NOT active")
                    # Debug: check what IS active
                    active_link = page.locator("#toc-list a.active")
                    if active_link.count() > 0:
                        print(f"Currently active: {active_link.get_attribute('href')}")
            else:
                print("Link href invalid")

        # Take screenshot of the TOC sidebar
        # We try to screenshot the viewport to see the TOC highlighting
        page.screenshot(path="verification/toc_active.png")
        print("Screenshot saved to verification/toc_active.png")

        browser.close()

if __name__ == "__main__":
    run()
