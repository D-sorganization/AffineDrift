from playwright.sync_api import sync_playwright


def verify_focus_visible() -> None:
    """
    Verifies the accessibility focus indicators on the website.

    This script launches a headless browser, navigates to the homepage,
    checks for the existence of the `:focus-visible` CSS rule, performs
    visual verification by tabbing through elements and capturing screenshots,
    and inspects the computed styles of the active element to ensure
    focus outlines are correctly applied.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("http://localhost:8000/index.html")

        # 1. Verify CSS Rule Existence - Check selector text exactly as it might appear
        rule_exists = page.evaluate(
            """() => {
            for (let sheet of document.styleSheets) {
                try {
                    for (let rule of sheet.cssRules) {
                        if (rule.selectorText === ':focus-visible') {
                            return rule.cssText;
                        }
                    }
                } catch(e) {}
            }
            return "NOT FOUND";
        }""",
        )
        print(f"CSS Rule Found: {rule_exists}")

        # 2. Visual verification
        # Click body to ensure focus context
        page.click("body")

        # Tab to skip link (1st tab)
        page.keyboard.press("Tab")
        page.wait_for_timeout(200)  # Wait for transition/render
        page.screenshot(path="verification/focus_01_skip.png")

        # Tab to Logo (2nd tab)
        page.keyboard.press("Tab")
        page.wait_for_timeout(200)
        page.screenshot(path="verification/focus_02_logo.png")

        # Tab to Home (3rd tab)
        page.keyboard.press("Tab")
        page.wait_for_timeout(200)
        page.screenshot(path="verification/focus_03_home.png")

        # 3. Check computed style of active element
        computed = page.evaluate(
            """() => {
            const el = document.activeElement;
            const style = window.getComputedStyle(el);
            return {
                tag: el.tagName,
                text: el.textContent ? el.textContent.substring(0, 20) : "no text",
                color: style.outlineColor,
                width: style.outlineWidth,
                style: style.outlineStyle,
                offset: style.outlineOffset
            };
        }""",
        )
        print(f"Computed Focus Styles: {computed}")

        browser.close()


if __name__ == "__main__":
    verify_focus_visible()
