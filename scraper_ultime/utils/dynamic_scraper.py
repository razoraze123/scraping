from __future__ import annotations

import random
import time
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from .logger import setup_logger


class DynamicFetcher:
    """Fetch pages using Selenium with basic anti-bot measures."""

    def __init__(self, headless: bool = True, chrome_driver_path: Optional[str] = None) -> None:
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        service = Service(chrome_driver_path) if chrome_driver_path else Service()
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        self.logger = setup_logger(__name__)

    def fetch(self, url: str) -> str:
        self.logger.info("Fetching %s", url)
        self.driver.get(url)
        self._scroll_page()
        time.sleep(random.uniform(1, 2))
        return self.driver.page_source

    def _scroll_page(self) -> None:
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )

    def close(self) -> None:
        self.driver.quit()
