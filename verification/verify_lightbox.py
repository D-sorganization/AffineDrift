
from playwright.sync_api import sync_playwright

def verify_lightbox_focus():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load the articles page (local file)
        # Note: We assume the build is correct or we use source files if possible.
        # Since we modified script.js, we need to test a page that includes it.
        # docs/articles.html is a good candidate.
        # We need to make sure the path is absolute for file://
        import os
        cwd = os.getcwd()
        page.goto(f'file://{cwd}/docs/articles/affine-nature-golf-swing.html')

        # Inject script.js if it's not loading correctly from file:// due to relative paths
        # But usually relative paths work. Let's try.

        # Wait for page load
        page.wait_for_load_state('networkidle')

        # Find an image to click
        # The script.js adds .zoomable class
        # We might need to inject our modified script.js content if the page loads the old one?
        # No, the file system is updated.

        image = page.locator('#quarto-document-content img').first
        if not image.count():
            print('No images found on page')
            return

        print('Clicking image...')
        image.click()

        # Wait for lightbox
        lightbox = page.locator('.lightbox-overlay')
        lightbox.wait_for(state='visible')

        # CHECK FOCUS
        focused = page.evaluate('document.activeElement.className')
        print(f'Active element class after open: {focused}')

        # Take screenshot of open lightbox
        page.screenshot(path='verification/lightbox_open.png')

        # Close lightbox via click
        print('Closing lightbox...')
        lightbox.click()

        # Wait for close
        lightbox.wait_for(state='hidden')

        # CHECK FOCUS RESTORATION
        # The image might not have a class if it wasn't .zoomable originally,
        # but script.js adds .zoomable.
        # However, activeElement might be the body if focus is lost.
        focused_after = page.evaluate('document.activeElement.tagName')
        print(f'Active element tag after close: {focused_after}')

        page.screenshot(path='verification/lightbox_closed.png')

        browser.close()

if __name__ == '__main__':
    verify_lightbox_focus()
