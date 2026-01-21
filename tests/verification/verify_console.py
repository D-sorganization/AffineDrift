import os

from playwright.sync_api import sync_playwright


def test_console_logs() -> None:
    cwd = os.getcwd()
    url = f"file://{cwd}/docs/index.html"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        logs: list[str] = []
        def on_console(msg: object) -> None:
            # Playwright msg has typed properties, but in callback we just hint loosely or specific
            # Using 'Any' or proper types if imported. msg is ConsoleMessage.
            # But let's use dynamic access or 'Any' to avoid deep imports if not needed,
            # or just 'msg' without type if we can avoid untyped error.
            # Actually, the error was 'Function is missing a type annotation'.
            # msg is likely ConsoleMessage.
            text = getattr(msg, "text", str(msg))
            logs.append(text)
            type_str = getattr(msg, "type", "info")
            print(f"Console {type_str}: {text}")

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
                raise AssertionError(
                    "Found banned console log: 'Mathematical notation rendering via MathJax'"
                )

        print("Verification passed: No banned logs found.")

        page.screenshot(path="tests/verification/verification.png")


if __name__ == "__main__":
    test_console_logs()
