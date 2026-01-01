
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

        # Just use keyboard to trigger. It's more reliable if overlay is blocking clicks.
        # Wait, if overlay is blocking clicks, it means lightbox is already open?
        # The logs said lightbox-overlay active intercepts pointer events.
        # This means lightbox IS OPEN covering the image.
        # Why is it open? Maybe my manual injection triggered it?
        # Or maybe the page load logic triggered it?

        # Let's check if active.
        active = page.evaluate('document.querySelector(".lightbox-overlay.active") !== null')
        print(f'Lightbox already active? {active}')

        if active:
             # Just check focus then
             pass
        else:
             # Try to open
             # Use keyboard to avoid overlay issues?
             # Inject unique image
            page.evaluate("""
               // Logic to create image and listeners
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

        # Close (click center of screen)
        # Use page.mouse to click somewhere on overlay
        page.mouse.click(500, 500)
        page.wait_for_timeout(200)

        restored_focus = page.evaluate('document.activeElement.id')
        print(f'Focus restored ID: {restored_focus}')

        page.screenshot(path='verification/lightbox_closed.png')

        browser.close()

if __name__ == '__main__':
    verify_lightbox_focus()
