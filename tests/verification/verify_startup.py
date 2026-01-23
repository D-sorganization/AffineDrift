import os

from playwright.sync_api import sync_playwright


def verify_startup():
    html_path = os.path.abspath("tests/verification/verify_startup.html")
    file_url = f"file://{html_path}"

    print(f"Loading {file_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Capture console logs to debug
        page.on("console", lambda msg: print(f"Console: {msg.text}"))

        page.goto(file_url)

        # Wait for startup to complete (splash screen usually takes some time)
        # CONFIG.MINIMUM_SPLASH_DURATION is 800ms
        # CONFIG.MAXIMUM_SPLASH_DURATION is 5000ms

        print("Waiting for startup to complete...")

        # Wait for isReady to be true, or timeout after 6 seconds
        try:
            page.wait_for_function("window.AffineDriftStartup && window.AffineDriftStartup.isReady() === true", timeout=6000)
            print("SUCCESS: AffineDriftStartup.isReady() became true.")
        except Exception as e:
            print(f"FAILURE: AffineDriftStartup.isReady() did not become true within timeout. Error: {e}")
            # Check current state
            is_ready = page.evaluate("window.AffineDriftStartup ? window.AffineDriftStartup.isReady() : 'undefined'")
            print(f"Current isReady state: {is_ready}")

        # Check metrics
        metrics = page.evaluate("window.AffineDriftMetrics")
        if metrics:
            print("Metrics found:")
            summary = metrics.get('summary', {})
            has_nan = False
            for key, value in summary.items():
                print(f"  {key}: {value}")
                if "NaN" in str(value) or "null" in str(value):
                    has_nan = True

            if has_nan:
                print("FAILURE: Metrics contain NaN or null values.")
            else:
                print("SUCCESS: Metrics look valid.")
        else:
            print("FAILURE: window.AffineDriftMetrics is undefined.")

        browser.close()

if __name__ == "__main__":
    verify_startup()
