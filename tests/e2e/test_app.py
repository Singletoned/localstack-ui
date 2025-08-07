import os

from playwright.sync_api import sync_playwright


def test_homepage():
    """Simple test to check homepage loads"""
    base_url = os.getenv("BASE_URL", "https://food-diary-nginx")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        try:
            page.goto(base_url, timeout=30000)
            title = page.title()
            assert title == "Food Diary Entry"
        finally:
            browser.close()


if __name__ == "__main__":
    test_homepage()

