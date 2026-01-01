
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

        # Manually create the lightbox logic
        # Note: In e.target context, e must be the event.
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

           window.triggerLightbox = function(e) {
             const img = e.currentTarget; // Use currentTarget to be safe
             lastFocusedElement = document.activeElement;

             const clone = img.cloneNode();
             lightbox.innerHTML = '';
             lightbox.appendChild(clone);
             lightbox.classList.add('active');
             lightbox.setAttribute('aria-hidden', 'false');

             lightbox.focus();
           };
        """)

        # Inject image
        page.evaluate("""
            const img = document.createElement('img');
            img.src = '../logo/logo_transparent_1.png';
            img.className = 'test-image';
            img.style.width = '200px';
            img.tabIndex = 0;
            document.body.appendChild(img);
            img.focus();
            img.onclick = window.triggerLightbox;
        """)

        initial_focus = page.evaluate('document.activeElement.className')
        print(f'Initial focus class: {initial_focus}')

        # Trigger click
        page.locator('.test-image').click()

        lightbox = page.locator('.lightbox-overlay')
        lightbox.wait_for(state='visible', timeout=5000)

        page.wait_for_timeout(100)

        active_el_class = page.evaluate('document.activeElement.className')
        print(f'Focus inside lightbox: {active_el_class}')

        page.screenshot(path='verification/lightbox_open.png')

        lightbox.click()
        page.wait_for_timeout(100)

        restored_focus = page.evaluate('document.activeElement.className')
        print(f'Focus restored: {restored_focus}')

        page.screenshot(path='verification/lightbox_closed.png')

        browser.close()

if __name__ == '__main__':
    verify_lightbox_focus()
