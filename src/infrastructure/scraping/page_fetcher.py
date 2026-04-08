import time
import random
from src.infrastructure.scraping.browser import Browser


class PageFetcher:
    """Fetches raw HTML with a random delay."""

    def __init__(self, browser: Browser, wait_range: tuple[int, int]):
        self._browser = browser
        self._wait_range = wait_range

    def fetch(self, url: str) -> str:
        self._browser.tab.get(url)
        time.sleep(random.uniform(*self._wait_range))
        return self._browser.tab.html
