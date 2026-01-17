from playwright.sync_api import sync_playwright
import os

def test_optimizations():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load a local article file
        cwd = os.getcwd()
        page.goto(f"file://{cwd}/docs/articles/theory-part1.html")

        # Verify Contact Form Feedback (document.forms)
        # We need to find a form or check if the code runs without error.
        # Since we modified the initialization logic, checking console logs for errors is key.

        # Check console for errors
        page.on("console", lambda msg: print(f"Console: {msg.text}"))

        # Wait for hydration
        page.wait_for_timeout(1000)

        # Check if lightbox initialized (it adds 'zoomable' class to images)
        # We modified initLightbox to use getElementsByTagName

        # Check if an image inside quarto-document-content has zoomable class
        # theory-part1.html should have images

        # Find an image
        images = page.locator("#quarto-document-content img")
        count = images.count()
        print(f"Found {count} images")

        if count > 0:
            first_image = images.first
            # Verify class contains 'zoomable'
            classes = first_image.get_attribute("class")
            print(f"Image classes: {classes}")
            if "zoomable" in classes:
                print("SUCCESS: Lightbox initialized (zoomable class added)")
            else:
                print("FAILURE: Lightbox NOT initialized")

        # Verify Email Copy (document.links)
        # We need a mailto link. theory-part1 might not have one, but contact.html does.

        page.goto(f"file://{cwd}/docs/contact.html")
        page.wait_for_timeout(1000)

        mailto_links = page.locator('a[href^="mailto:"]')
        mailto_count = mailto_links.count()
        print(f"Found {mailto_count} mailto links")

        if mailto_count > 0:
            # Check if copy button exists after the link
            # The script adds a button.copy-email-btn after the link
            first_link = mailto_links.first
            # We can check if the next sibling is the button
            # Playwright doesn't have direct next_sibling, but we can check if .copy-email-btn exists

            buttons = page.locator(".copy-email-btn")
            btn_count = buttons.count()
            print(f"Found {btn_count} copy-email-btn buttons")

            if btn_count > 0:
                print("SUCCESS: Email copy button added")
            else:
                print("FAILURE: Email copy button NOT added")

        # Take screenshot
        page.screenshot(path="verification/optimization_verification.png")

        browser.close()

if __name__ == "__main__":
    test_optimizations()
