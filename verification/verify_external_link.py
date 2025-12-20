import os

from playwright.sync_api import sync_playwright


def run():
    os.makedirs("verification", exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        url = "http://localhost:8000/resources-websites.html"
        print(f"Navigating to {url}")

        page.goto(url)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        # Find external links
        links = page.locator("a.external-link")
        count = links.count()
        print(f"Found {count} links with class 'external-link'")

        if count > 0:
            # Try to find a visible one
            for i in range(count):
                link = links.nth(i)
                if link.is_visible():
                    href = link.get_attribute('href')
                    print(f"Scrolling to visible link {i}: {href}")
                    link.scroll_into_view_if_needed()
                    page.screenshot(path="verification/external_links.png")
                    print("Screenshot saved to verification/external_links.png")
                    break
            else:
                 print("No visible external links found to screenshot")
        else:
            print("FAILURE: No external links found with class")

        browser.close()

if __name__ == "__main__":
    run()
