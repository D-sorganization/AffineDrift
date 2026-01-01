
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

        page.evaluate("""
           let lastFocusedElement = null;

           const existing = document.querySelector('.lightbox-overlay');
           if (existing) existing.remove();

           const lightbox = document.createElement('div');
           lightbox.className = 'lightbox-overlay';
           lightbox.setAttribute('tabindex', '-1');

           // Ensure styling is forced for test
           lightbox.style.outline = 'none';
           lightbox.style.position = 'fixed';
           lightbox.style.top = '0';
           lightbox.style.left = '0';
           lightbox.style.width = '100%';
           lightbox.style.height = '100%';
           lightbox.style.zIndex = '2000';
           lightbox.style.display = 'none'; // Initially hidden

           lightbox.addEventListener('click', () => {
             lightbox.style.display = 'none';
             if (lastFocusedElement) {
               lastFocusedElement.focus();
               lastFocusedElement = null;
             }
           });
           document.body.appendChild(lightbox);

           window.triggerLightbox = function() {
             console.log('Triggering lightbox');
             const img = document.activeElement;
             lastFocusedElement = img;

             lightbox.style.display = 'block'; // Make visible

             // Check if connected and visible
             console.log('Is visible?', lightbox.offsetParent !== null);

             console.log('Focusing lightbox...');
             lightbox.focus();
             console.log('Active element is now:', document.activeElement.className);
           };

           const img = document.createElement('img');
           img.src = '../logo/logo_transparent_1.png';
           img.id = 'unique-test-img-final';
           img.className = 'test-image';
           img.style.width = '200px';
           img.tabIndex = 0;
           document.body.appendChild(img);
           img.focus();
           img.onclick = window.triggerLightbox;
        """)

        page.keyboard.press('Enter')
        page.wait_for_timeout(500)

        # Check focus
        active_el_class = page.evaluate('document.activeElement.className')
        print(f'Focus inside lightbox: {active_el_class}')

        page.screenshot(path='verification/lightbox_open.png')

        # Close
        page.mouse.click(500, 500)
        page.wait_for_timeout(200)

        restored_focus = page.evaluate('document.activeElement.id')
        print(f'Focus restored ID: {restored_focus}')

        page.screenshot(path='verification/lightbox_closed.png')

        browser.close()

if __name__ == '__main__':
    verify_lightbox_focus()
