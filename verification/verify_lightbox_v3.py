
from playwright.sync_api import sync_playwright
import os
import shutil

def verify_lightbox_focus():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Ensure script.js is available
        shutil.copy('script.js', 'docs/script.js')
        if not os.path.exists('docs/articles'):
            os.makedirs('docs/articles')
        shutil.copy('script.js', 'docs/articles/script.js')

        cwd = os.getcwd()
        url = f'file://{cwd}/docs/articles/affine-nature-golf-swing.html'

        page.goto(url)
        page.wait_for_load_state('domcontentloaded') # Faster than networkidle

        # Inject a test image since the article might not have one in the body
        page.evaluate("""
            const img = document.createElement('img');
            img.src = '../logo/logo_transparent_1.png';
            img.className = 'test-image';
            img.style.width = '200px';
            document.getElementById('quarto-document-content').appendChild(img);

            // Re-run the script initialization logic for this image?
            // script.js runs on DOMContentLoaded. If we add image later, it won't have .zoomable.
            // But we can trigger the logic manually or reload script?
            // Actually, script.js adds listeners to existing images.
            // Let's reload the script logic or just emulate the structure.

            // Re-run the setup part of script.js? No, easier to just reload page with image?
            // Cannot modify file.

            // Let's manually trigger the setup code for the new image
            const contentImages = document.querySelectorAll('#quarto-document-content img');
            contentImages.forEach((img) => {
                if (img.closest('a') || img.closest('button')) return;
                img.classList.add('zoomable');
                img.setAttribute('tabindex', '0');
                img.setAttribute('role', 'button');
                img.setAttribute('aria-label', 'Zoom image');
            });
        """)

        # Click the image
        page.locator('.test-image').click()

        lightbox = page.locator('.lightbox-overlay')
        lightbox.wait_for(state='visible')

        page.wait_for_timeout(200)

        # Check focus
        active_el_class = page.evaluate('document.activeElement.className')
        print(f'Active element class: {active_el_class}')

        page.screenshot(path='verification/lightbox_open.png')

        # Close
        lightbox.click()
        page.wait_for_timeout(200)

        page.screenshot(path='verification/lightbox_closed.png')

        browser.close()

if __name__ == '__main__':
    verify_lightbox_focus()
