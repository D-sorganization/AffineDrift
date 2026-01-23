import os
import time
import re
from playwright.sync_api import sync_playwright, expect

def verify_startup():
    cwd = os.getcwd()
    fixture_path = os.path.join(cwd, "tests/verification/startup_fixture.html")
    url = f"file://{fixture_path}"

    print(f"Loading {url}...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        console_logs = []
        page.on("console", lambda msg: console_logs.append(msg.text))

        page.goto(url)

        # 1. Verify Splash Screen is Prepended (First Child)
        print("Verifying splash screen injection...")
        # Wait for splash to exist
        splash = page.locator("#ad-splash-screen")
        expect(splash).to_be_visible(timeout=5000)

        # Check if it is the first child of body
        is_first_child = page.evaluate("""
            () => {
                const splash = document.getElementById('ad-splash-screen');
                return document.body.firstElementChild === splash;
            }
        """)
        if not is_first_child:
            print("FAILURE: Splash screen is NOT the first child of body.")
        else:
            print("PASSED: Splash screen is the first child.")

        # 2. Verify Progress Bar Animation
        print("Verifying progress bar animation...")
        # Wait a bit for animation loop to run
        page.wait_for_timeout(1000)
        progress_width = page.evaluate("""
            () => {
                const bar = document.getElementById('ad-splash-progress-bar');
                return bar ? bar.style.width : '0%';
            }
        """)
        print(f"Progress bar width: {progress_width}")
        # If width is 0%, it means the interval didn't update the style, likely because state.progressElement was null.
        if progress_width == '0%' or not progress_width:
             print("FAILURE: Progress bar width is 0%. Fix for progressElement likely needed.")

        # 3. Wait for Startup to be Ready (or force it)
        print("Waiting for splash to hide...")
        # Force hide to ensure we reach the end state if metrics take too long
        page.evaluate("if(window.AffineDriftStartup && window.AffineDriftStartup.forceHide) window.AffineDriftStartup.forceHide()")

        # Wait for hidden class
        # Note: class list might be "ad-splash-screen ad-splash-exit ad-splash-hidden"
        expect(splash).to_have_class(re.compile(r"ad-splash-hidden"))
        print("Splash screen hidden.")

        # 4. Verify isReady is true
        print("Verifying isReady state...")
        is_ready = page.evaluate("window.AffineDriftStartup.isReady()")
        if is_ready:
            print("PASSED: window.AffineDriftStartup.isReady() is true.")
        else:
            print("FAILURE: window.AffineDriftStartup.isReady() is false.")

        # 5. Check Console Logs for NaN and 0.00ms errors
        print("Checking console logs...")
        found_issue = False
        for log in console_logs:
            if "NaN" in log:
                print(f"FAILURE: Found NaN in log: {log}")
                found_issue = True
            # Check for suspicious 0.00ms that implies missing data (except Navigation Start which is 0)
            # "First Paint: 0.00ms" is suspicious if not caught.
            # But "Navigation Start to DOM Ready: 0.00ms" might be valid if fast.
            # However, "First Paint: N/A" is preferred over 0.00ms if null.

        if not found_issue:
            print("PASSED: No obvious issues in logs.")

        browser.close()

if __name__ == "__main__":
    verify_startup()
