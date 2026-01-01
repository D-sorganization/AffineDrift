
from playwright.sync_api import sync_playwright
import os
import shutil

def verify_lightbox_focus():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # We need to make sure the script.js in docs/ is the updated one.
        # Since I edited script.js in the root, and the site build process
        # normally copies it to docs/, I should manually copy it for verification
        # to ensure the html file sees the changes if it's loading relative.

        shutil.copy('script.js', 'docs/script.js')

        # docs/articles/affine-nature-golf-swing.html loads script.js from root?
        # No, it loads <script src="script.js"></script>.
        # Wait, the file I read has <script src="script.js"></script> at the end.
        # If the file is in docs/articles/, then src="script.js" looks in docs/articles/script.js.
        # But I see script.js in docs/ (root of docs).

        # Let's check if docs/articles/script.js exists.
        if not os.path.exists('docs/articles/script.js'):
            # If not, the HTML might be expecting it there, or I misread the structure.
            # If the HTML is generated, maybe it puts script.js there?
            # Let's copy it there just in case for the test.
            if not os.path.exists('docs/articles'):
                os.makedirs('docs/articles')
            shutil.copy('script.js', 'docs/articles/script.js')

        cwd = os.getcwd()
        url = f'file://{cwd}/docs/articles/affine-nature-golf-swing.html'
        print(f'Navigating to {url}')

        page.goto(url)
        page.wait_for_load_state('networkidle')

        # Find images
        images = page.locator('#quarto-document-content img')
        count = images.count()
        print(f'Found {count} images')

        if count == 0:
            # If no images, maybe this page doesn't have any.
            # Let's inject one for testing purposes if needed, or pick another page.
            # But let's check page content.
            pass
        else:
            image = images.first
            print('Clicking image...')
            image.click()

            lightbox = page.locator('.lightbox-overlay')
            lightbox.wait_for(state='visible')

            # Check focus
            # We need to wait a tick for focus to move?
            page.wait_for_timeout(100)

            active_el_class = page.evaluate('document.activeElement.className')
            print(f'Active element class: {active_el_class}')

            page.screenshot(path='verification/lightbox_open.png')

            # Close
            lightbox.click()
            page.wait_for_timeout(100)

            page.screenshot(path='verification/lightbox_closed.png')

if __name__ == '__main__':
    verify_lightbox_focus()
