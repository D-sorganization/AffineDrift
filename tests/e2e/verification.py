from playwright.sync_api import sync_playwright
import os
import shutil

def run_cuj(page):
    page.goto(f"file://{os.getcwd()}/offline.html")
    page.wait_for_timeout(500)

    # We're just verifying that the accessibility ARIA labels are present on the elements.

    nav_count = page.evaluate('document.querySelectorAll("nav[aria-label]").length')
    print(f"Navs with aria-label: {nav_count}")

    aside_count = page.evaluate('document.querySelectorAll("aside[aria-label]").length')
    print(f"Asides with aria-label: {aside_count}")

    main_count = page.evaluate('document.querySelectorAll("main[aria-label]").length')
    print(f"Mains with aria-label: {main_count}")

    # Take screenshot at the key moment
    page.screenshot(path="/home/jules/verification/screenshots/verification.png")
    page.wait_for_timeout(1000)  # Hold final state for the video

if __name__ == "__main__":
    os.makedirs("/home/jules/verification/videos", exist_ok=True)
    os.makedirs("/home/jules/verification/screenshots", exist_ok=True)

    # Clean up previous videos
    shutil.rmtree("/home/jules/verification/videos", ignore_errors=True)
    os.makedirs("/home/jules/verification/videos", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir="/home/jules/verification/videos"
        )
        page = context.new_page()
        try:
            run_cuj(page)
        finally:
            context.close()  # MUST close context to save the video
            browser.close()
