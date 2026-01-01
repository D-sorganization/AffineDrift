
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

        # CLEAR BODY to be safe from duplicates (seems like I have multiple copies of elements?)
        # Ah, maybe because of previous failed runs not clearing state? No, new page object.
        # Maybe the page itself has duplicates? Or my injection logic is flawed.
        # Let's verify how many unique-test-img exist before I click.

        page.evaluate("""
           let lastFocusedElement = null;

           // Remove existing overlay
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

        # Inject ONE image
        page.evaluate("""
            // Remove any existing
            const existingImgs = document.querySelectorAll('#unique-test-img');
            existingImgs.forEach(img => img.remove());

            const img = document.createElement('img');
            img.src = '../logo/logo_transparent_1.png';
            img.id = 'unique-test-img';
            img.className = 'test-image';
            img.style.width = '200px';
            img.tabIndex = 0;
            document.body.appendChild(img);
            img.focus();
            img.onclick = window.triggerLightbox;
        """)

        # Verify count
        count = page.locator('#unique-test-img').count()
        print(f'Image count: {count}')

        if count > 1:
            print('Still > 1 image. Why? Maybe inside shadow DOM or frames?')
            # Let's pick the last one
            target = page.locator('#unique-test-img').last
        else:
            target = page.locator('#unique-test-img')

        target.click()

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
