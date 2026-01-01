
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
        page.wait_for_load_state('domcontentloaded')

        # Inject script.js manually to ensure it runs?
        # If it ran, .lightbox-overlay should exist in DOM (even if hidden).

        exists = page.evaluate("document.querySelector('.lightbox-overlay') !== null")
        print(f'Lightbox overlay exists: {exists}')

        if not exists:
            print('Injecting script.js content manually...')
            with open('script.js', 'r') as f:
                js_content = f.read()
            page.evaluate(js_content)

        # Inject image
        page.evaluate("""
            const img = document.createElement('img');
            img.src = '../logo/logo_transparent_1.png';
            img.className = 'test-image';
            img.style.width = '200px';
            document.getElementById('quarto-document-content').appendChild(img);

            // Re-run setup
            const contentImages = document.querySelectorAll('#quarto-document-content img');
            contentImages.forEach((img) => {
                if (img.closest('a') || img.closest('button')) return;
                img.classList.add('zoomable');
                img.setAttribute('tabindex', '0');
                img.setAttribute('role', 'button');
                img.setAttribute('aria-label', 'Zoom image');
            });
        """)

        # Trigger click
        page.locator('.test-image').click()

        lightbox = page.locator('.lightbox-overlay')
        lightbox.wait_for(state='visible', timeout=5000)

        page.wait_for_timeout(200)

        active_el_class = page.evaluate('document.activeElement.className')
        print(f'Active element class: {active_el_class}')

        page.screenshot(path='verification/lightbox_open.png')

        lightbox.click()
        page.wait_for_timeout(200)

        active_el_class_after = page.evaluate('document.activeElement.className')
        print(f'Active element class after close: {active_el_class_after}')

        page.screenshot(path='verification/lightbox_closed.png')

        browser.close()

if __name__ == '__main__':
    verify_lightbox_focus()
