
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

        page.on('console', lambda msg: print(f'PAGE LOG: {msg.text}'))

        # Try interacting first to make document focusable?
        page.mouse.click(10, 10)

        page.evaluate("""
           const lightbox = document.createElement('div');
           lightbox.className = 'lightbox-overlay';
           lightbox.tabIndex = -1;

           lightbox.style.position = 'fixed';
           lightbox.style.top = '0';
           lightbox.style.left = '0';
           lightbox.style.width = '100%';
           lightbox.style.height = '100%';
           lightbox.style.zIndex = '2000';

           document.body.appendChild(lightbox);
        """)

        # Focus from python side
        page.locator('.lightbox-overlay').focus()

        active = page.evaluate('document.activeElement.className')
        print(f'Active after playwright focus: {active}')

        page.screenshot(path='verification/lightbox_open.png')
        browser.close()

if __name__ == '__main__':
    verify_lightbox_focus()
