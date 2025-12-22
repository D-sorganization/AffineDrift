from playwright.sync_api import Page, expect, sync_playwright


def test_toc_and_history(page: Page) -> None:  # type: ignore[no-any-unimported, unused-ignore]
    """
    Verifies that the Table of Contents and Article History are generated correctly.

    This test checks for the presence and content of the TOC and history list on
    articles.html and ensures the history tracking logic works.
    """
    # Visit articles.html to check TOC and History
    print("Navigating to articles.html...")
    page.goto("http://localhost:8000/articles.html")

    # Check "On This Page" TOC
    print("Checking TOC...")
    # It should be injected by script.js
    toc_list = page.locator("#toc-list")

    # It might take a moment if it's dynamic
    expect(toc_list).to_be_visible()

    # Check if TOC has items (should pick up article categories)
    expect(toc_list.locator("li")).not_to_have_count(0)
    print("TOC verified.")

    # Check history list
    print("Checking History list...")
    history_list = page.locator("#articles-history-list")
    expect(history_list).to_be_visible()

    # We haven't visited any articles yet in this session,
    # so history might be "No recent articles yet"
    # Or we can visit one first.

    print("Navigating to an article to populate history...")
    page.goto("http://localhost:8000/articles/theory-part1.html")

    print("Navigating back to articles.html...")
    page.goto("http://localhost:8000/articles.html")

    # Now verify history has the item
    # Note: script.js logic for history title extraction might differ slightly from
    # exact string "Theory Part 1"
    # It strips "AffineDrift - " etc.
    # The title of theory-part1.html is
    # "Affine Control Interpretation of the Golf Swing – AffineDrift"
    # So it should be "Affine Control Interpretation of the Golf Swing"

    expect(history_list).to_contain_text("Affine Control Interpretation")
    print("History verified.")

    page.screenshot(path="/home/jules/verification/history.png")


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            test_toc_and_history(page)
        except Exception as e:
            print(f"Verification failed: {e}")
            page.screenshot(path="/home/jules/verification/error.png")
            raise e
        finally:
            browser.close()
