import json
from DrissionPage import Chromium
from loguru import logger


class Browser:
    """Owns Chromium instance and cookie setup."""

    def __init__(self, cookies_file: str):
        self._cookies_file = cookies_file
        self.instance = Chromium()
        self.tab = self.instance.new_tab()

    def apply_cookies(self) -> None:
        with open(self._cookies_file, encoding="utf-8") as f:
            self.tab.set.cookies(json.load(f))
        logger.info("Cookies applied")
