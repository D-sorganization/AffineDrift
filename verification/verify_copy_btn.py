from playwright.sync_api import sync_playwright

def verify_copy_button():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(permissions=['clipboard-read', 'clipboard-write'])
        page = context.new_page()

        page.goto("http://localhost:8001/articles/secondary-axis-stability.html")
        page.wait_for_timeout(2000)

        wrapper_count = page.locator(".code-wrapper").count()
        print(f"Found {wrapper_count} code-wrapper elements.")

        # Check if button exists in DOM
        button_locator = page.locator('.code-wrapper button.copy-btn')
        btn_count = button_locator.count()
        print(f"Found {btn_count} copy buttons.")

        if btn_count > 0:
            first_btn = button_locator.first
            # Check attributes
            print("Button attributes:", first_btn.evaluate("el => el.outerHTML"))

            # Click it
            first_btn.click()

            # Check for copied state
            try:
                page.wait_for_selector('button.copy-btn.copied', timeout=3000)
                print("Success: Button changed to Copied!")
                page.screenshot(path="verification/copy_success.png")
            except:
                print("Failed to see Copied state.")
        else:
            print("No buttons found inside wrappers.")

        browser.close()

if __name__ == "__main__":
    verify_copy_button()
