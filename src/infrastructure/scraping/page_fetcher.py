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
        self._scroll()
        return self._browser.tab.html

    def _scroll(self) -> None:
        tab = self._browser.tab
        for _ in range(5):
            tab.scroll.down(300)
            time.sleep(random.uniform(0.3, 0.7))
