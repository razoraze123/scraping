import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class DynamicFetcher:
    """Fetch pages using Selenium for sites with heavy JavaScript."""

    def __init__(self, headless: bool = True):
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options)

    def fetch(self, url: str) -> str:
        """Return page HTML after JS execution."""
        self.driver.get(url)
        time.sleep(2)
        return self.driver.page_source

    def close(self):
        self.driver.quit()
