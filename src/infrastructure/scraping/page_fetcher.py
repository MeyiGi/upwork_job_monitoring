import time
from src.infrastructure.scraping.browser import Browser

_CARD_SELECTOR = "css:section.air3-card-section"


class PageFetcher:
    """Fetches raw HTML, waiting for job cards to appear."""

    def __init__(self, browser: Browser, wait_range: tuple[int, int] = (0, 0)):
        self._browser = browser

    def fetch(self, url: str) -> str:
        tab = self._browser.tab
        tab.set.load_mode.eager()
        tab.get(url)
        tab.ele(_CARD_SELECTOR, timeout=15)
        self._scroll()
        return tab.html

    def _scroll(self) -> None:
        tab = self._browser.tab
        for _ in range(3):
            tab.scroll.down(400)
            time.sleep(0.3)
