import logging
import os
import sys

from playwright.sync_api import sync_playwright

# Get logger
logger = logging.getLogger(__name__)


def verify_startup():
    """Verify the startup launcher functionality using Playwright."""
    cwd = os.getcwd()
    url = f"file://{cwd}/tests/verification/test_startup.html"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Capture console logs
        logs = []
        page.on("console", lambda msg: logs.append(msg.text))

        logger.info(f"Navigating to {url}")
        page.goto(url)

        # Wait for splash screen to appear
        try:
            page.wait_for_selector("#ad-splash-screen", state="attached", timeout=1000)
        except Exception:
            logger.error("Splash screen not found!")
            sys.exit(1)

        logger.info("Splash screen found.")

        # Check progress bar update (waiting a bit for animation)
        page.wait_for_timeout(500)

        # Take screenshot of splash screen
        page.screenshot(path="tests/verification/splash_screen.png")
        logger.info("Screenshot saved to tests/verification/splash_screen.png")

        width = page.evaluate("document.getElementById('ad-splash-progress-bar').style.width")
        logger.info(f"Progress bar width: '{width}'")

        if not width or width == "0%":
            logger.error("FAIL: Progress bar did not move! (Likely state.progressElement is null)")
            # We don't exit here to check other things, but we flag it
            progress_failed = True
        else:
            progress_failed = False

        # Wait for splash to disappear (max 5s, but usually faster)
        # We wait for hidden class
        try:
            page.wait_for_selector("#ad-splash-screen.ad-splash-hidden", timeout=6000)
            logger.info("Splash screen hidden.")
        except Exception:
            logger.error("Splash screen did not hide!")

        # Check isReady
        is_ready = page.evaluate("window.AffineDriftStartup && window.AffineDriftStartup.isReady()")
        logger.info(f"isReady(): {is_ready}")

        if not is_ready:
            logger.error("FAIL: Startup launcher isReady() returned False!")

        if progress_failed or not is_ready:
            sys.exit(1)

        logger.info("Verification passed!")
        browser.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        verify_startup()
    except SystemExit as e:
        sys.exit(e.code)
    except Exception as e:
        logger.error(f"Verification failed with exception: {e}")
        sys.exit(1)
