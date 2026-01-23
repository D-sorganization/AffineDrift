import logging
import os
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

def test_startup_launcher() -> None:
    cwd = os.getcwd()
    url = f"file://{cwd}/tests/verification/verify_startup.html"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        logs = []
        def on_console(msg):
            logs.append(msg.text)

        page.on("console", on_console)

        logger.info(f"Navigating to {url}")
        page.goto(url)

        # 1. Verify Splash Screen Insertion
        splash = page.locator("#ad-splash-screen")
        splash.wait_for(state="attached")
        assert splash.count() == 1, "Splash screen not found"

        is_first = page.evaluate("""() => {
            const splash = document.getElementById('ad-splash-screen');
            return document.body.firstElementChild === splash;
        }""")
        assert is_first, "Splash screen is not the first element in body"

        # 2. Verify state.progressElement is not null
        page.wait_for_timeout(500)
        progress_width = page.evaluate("""() => {
            const bar = document.getElementById('ad-splash-progress-bar');
            return bar ? bar.style.width : 'null';
        }""")
        print(f"Progress width: '{progress_width}'")
        assert progress_width and progress_width != 'null', "Progress bar not updating (width is empty or null)"

        # Take screenshot while splash is visible
        page.screenshot(path="tests/verification/splash_screen.png")

        # 3. Check isReady state
        page.wait_for_timeout(2500) # Wait for animation + extra

        is_hidden = page.evaluate("""() => {
             const splash = document.getElementById('ad-splash-screen');
             if (!splash) return true;
             return splash.classList.contains('ad-splash-hidden');
        }""")

        print(f"Splash is hidden/removed: {is_hidden}")

        # Check isReady
        is_ready = page.evaluate("window.AffineDriftStartup && window.AffineDriftStartup.isReady()")
        print(f"isReady: {is_ready}")

        # If splash is finished, isReady MUST be true
        if is_hidden:
            assert is_ready, "Splash is hidden but isReady() is false!"

        # 4. Verify Metrics
        metrics = page.evaluate("window.AffineDriftMetrics")
        if metrics:
            summary = metrics.get('summary', {})
            print(f"Metrics Summary: {summary}")
            for key, value in summary.items():
                assert 'NaN' not in value, f"Metric {key} is NaN: {value}"
                if 'ms' in value:
                    try:
                        val = float(value.replace('ms', ''))
                        assert val >= 0, f"Metric {key} is negative: {value}"
                    except ValueError:
                        pass
        else:
            print("No metrics found")

    print("Verification Passed")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_startup_launcher()
