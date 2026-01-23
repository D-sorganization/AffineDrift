import os
import sys
import asyncio
from playwright.async_api import async_playwright

async def run():
    print("Starting verification...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Construct file path
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'startup_test.html'))
        url = f'file://{file_path}'

        print(f"Loading {url}")

        # We need to capture console logs to debug and verify logic
        page.on("console", lambda msg: print(f"Browser Console: {msg.text}"))

        await page.goto(url)

        # 1. Verify API exists
        is_defined = await page.evaluate("typeof window.AffineDriftStartup !== 'undefined'")
        if is_defined:
            print("SUCCESS: window.AffineDriftStartup is defined")
        else:
            print("FAILURE: window.AffineDriftStartup is NOT defined")
            sys.exit(1)

        # 2. Check splash screen presence
        splash = await page.query_selector('#ad-splash-screen')
        if splash:
            print("SUCCESS: Splash screen found in DOM")
        else:
            print("FAILURE: Splash screen NOT found in DOM")
            sys.exit(1)

        # 3. Check progress bar element assignment (by checking if width changes)
        # If state.progressElement is null, the width style won't update
        print("Waiting for progress updates...")

        # Wait a bit for animation to start
        await asyncio.sleep(1)

        # Take a screenshot of the splash screen
        await page.screenshot(path="tests/verification/splash_screen.png")
        print("Screenshot saved to tests/verification/splash_screen.png")

        progress_width = await page.evaluate("""() => {
            const bar = document.getElementById('ad-splash-progress-bar');
            return bar ? bar.style.width : '0%';
        }""")

        print(f"Progress bar width: {progress_width}")

        if progress_width != '0%' and progress_width != '':
             print("SUCCESS: Progress bar is updating (state.progressElement is correct)")
        else:
             print("FAILURE: Progress bar width is 0% or empty (state.progressElement might be null)")
             # We don't exit here because we want to see other failures too,
             # but strictly this is a failure of the current code.

        # 4. Check isReady state
        # We force hide the splash to trigger completion
        print("Forcing splash hide to trigger completion...")
        await page.evaluate("window.AffineDriftStartup.forceHide()")

        # Wait for transition
        await asyncio.sleep(1)

        is_ready = await page.evaluate("window.AffineDriftStartup.isReady()")
        print(f"isReady state: {is_ready}")

        if is_ready:
            print("SUCCESS: isReady is true")
        else:
            print("FAILURE: isReady is false (Expected true)")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
