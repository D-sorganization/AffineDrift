from playwright.sync_api import sync_playwright
import os

def test_console_logs():
    cwd = os.getcwd()
    url = f"file://{cwd}/docs/index.html"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        logs = []
        def on_console(msg):
            logs.append(msg.text)
            print(f"Console {msg.type}: {msg.text}")

        page.on("console", on_console)

        print(f"Navigating to {url}")
        page.goto(url)

        # Wait a bit for scripts to execute
        page.wait_for_timeout(2000)

        # Check logs
        for log in logs:
            if "AffineDrift loaded successfully" in log:
                raise AssertionError("Found banned console log: 'AffineDrift loaded successfully'")
            if "Mathematical notation rendering via MathJax" in log:
                raise AssertionError("Found banned console log: 'Mathematical notation rendering via MathJax'")

        print("Verification passed: No banned logs found.")

        page.screenshot(path="tests/verification/verification.png")

if __name__ == "__main__":
    test_console_logs()
