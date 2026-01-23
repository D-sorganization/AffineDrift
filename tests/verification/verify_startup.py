import os
import time
from playwright.sync_api import sync_playwright

def test_startup():
    cwd = os.getcwd()

    # Create a dummy HTML file that loads the source script
    # Note: relative paths from tests/verification/ to src/
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Startup Verification</title>
        <!-- Use relative path to src/css/startup-launcher.css -->
        <link rel="stylesheet" href="../../src/css/startup-launcher.css">
        <!-- Use relative path to src/js/startup-launcher.js -->
        <script src="../../src/js/startup-launcher.js"></script>
    </head>
    <body>
        <div class="main-content-area">
            <h1>Content</h1>
            <p>Some dummy content to load.</p>
        </div>
    </body>
    </html>
    """

    # Ensure verification dir exists
    os.makedirs("tests/verification", exist_ok=True)

    html_path = os.path.join(cwd, "tests/verification/test_startup.html")
    with open(html_path, "w") as f:
        f.write(html_content)

    url = f"file://{html_path}"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            print(f"Navigating to {url}")
            page.goto(url)

            # Wait for splash screen to appear
            # Ideally it appears immediately because the script runs in head and prepends to body
            # But we might need to wait for DOM execution
            splash = page.locator("#ad-splash-screen")
            # If our fix worked, splash should be in DOM
            splash.wait_for(state="attached", timeout=5000)
            print("Splash screen found.")

            # Take screenshot of splash
            page.screenshot(path="tests/verification/splash_screen.png")
            print("Splash screen screenshot taken.")

            # Check progress element exists (verifying our querySelector fix)
            progress = page.locator("#ad-splash-progress-bar")
            progress.wait_for(state="attached", timeout=1000)
            print("Progress bar found.")

            # Check logic: Wait for isReady to become true
            # We can poll for it
            is_ready = False
            for i in range(20): # Try for 10 seconds
                is_ready = page.evaluate("() => window.AffineDriftStartup && window.AffineDriftStartup.isReady()")
                if is_ready:
                    print(f"isReady is true at iteration {i}")
                    break
                time.sleep(0.5)

            if not is_ready:
                # Debug info
                state_dump = page.evaluate("() => window.AffineDriftStartup && window.AffineDriftStartup.getMetrics()")
                print(f"Metrics dump: {state_dump}")
                raise AssertionError("window.AffineDriftStartup.isReady() never became true")

            print("isReady verified as true.")

            # Verify splash is eventually hidden
            # The script sets a timeout or waits for load. Since we have very little content, it should happen fast.
            # But MINIMUM_SPLASH_DURATION is 800ms.

            # It adds 'ad-splash-hidden' class
            page.wait_for_selector(".ad-splash-hidden", timeout=10000)
            print("Splash screen hidden (class added).")

            browser.close()
            print("Verification passed!")

    finally:
        # Cleanup
        if os.path.exists(html_path):
            os.remove(html_path)

if __name__ == "__main__":
    test_startup()
