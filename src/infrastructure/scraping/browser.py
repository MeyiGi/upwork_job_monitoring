import json
from DrissionPage import Chromium, ChromiumOptions
from loguru import logger


class Browser:
    """Owns Chromium instance and cookie setup."""

    def __init__(self, cookies_file: str):
        self._cookies_file = cookies_file
        co = ChromiumOptions()
        # co.set_argument('--headless')
        # co.set_argument('--no-sandbox')
        # co.set_argument('--disable-dev-shm-usage')
        # co.set_argument('--disable-gpu')
        # co.set_argument('--remote-allow-origins=*')
        co.set_browser_path('/usr/bin/google-chrome')

        self.instance = Chromium(co)
        self.tab = self.instance.new_tab()

    def apply_cookies(self) -> None:
        with open(self._cookies_file, encoding="utf-8") as f:
            self.tab.set.cookies(json.load(f))
        logger.info("Cookies applied")
