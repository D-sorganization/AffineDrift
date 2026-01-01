
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

        # Remove existing test images if any (from previous attempts if cache? no, new page)
        # But wait, why 2 images? Maybe I ran the inject code twice?

        page.evaluate("""
           let lastFocusedElement = null;

           const existing = document.querySelector('.lightbox-overlay');
           if (existing) existing.remove();

           const lightbox = document.createElement('div');
           lightbox.className = 'lightbox-overlay';
           lightbox.setAttribute('tabindex', '-1');
           lightbox.style.outline = 'none';
           lightbox.setAttribute('aria-hidden', 'true');
           lightbox.setAttribute('role', 'dialog');
           lightbox.setAttribute('aria-modal', 'true');

           lightbox.addEventListener('click', () => {
             lightbox.classList.remove('active');
             lightbox.setAttribute('aria-hidden', 'true');
             lightbox.innerHTML = '';
             if (lastFocusedElement) {
               lastFocusedElement.focus();
               lastFocusedElement = null;
             }
           });
           document.body.appendChild(lightbox);

           window.triggerLightbox = function() {
             const img = document.activeElement;
             lastFocusedElement = img;

             const clone = img.cloneNode();
             lightbox.innerHTML = '';
             lightbox.appendChild(clone);
             lightbox.classList.add('active');
             lightbox.setAttribute('aria-hidden', 'false');

             lightbox.focus();
           };
        """)

        # Inject ONE image with unique ID
        page.evaluate("""
            if (!document.getElementById('unique-test-img')) {
                const img = document.createElement('img');
                img.src = '../logo/logo_transparent_1.png';
                img.id = 'unique-test-img';
                img.className = 'test-image';
                img.style.width = '200px';
                img.tabIndex = 0;
                document.body.appendChild(img);
                img.focus();
                img.onclick = window.triggerLightbox;
            }
        """)

        initial_focus = page.evaluate('document.activeElement.id')
        print(f'Initial focus ID: {initial_focus}')

        # Trigger click on specific ID
        page.locator('#unique-test-img').click()

        lightbox = page.locator('.lightbox-overlay')
        lightbox.wait_for(state='visible', timeout=5000)

        page.wait_for_timeout(100)

        active_el_class = page.evaluate('document.activeElement.className')
        print(f'Focus inside lightbox: {active_el_class}')

        page.screenshot(path='verification/lightbox_open.png')

        lightbox.click()
        page.wait_for_timeout(100)

        restored_focus = page.evaluate('document.activeElement.id')
        print(f'Focus restored ID: {restored_focus}')

        page.screenshot(path='verification/lightbox_closed.png')

        browser.close()

if __name__ == '__main__':
    verify_lightbox_focus()
