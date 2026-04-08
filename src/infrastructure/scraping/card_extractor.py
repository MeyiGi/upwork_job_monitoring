from typing import List
from bs4 import BeautifulSoup, Tag


class CardExtractor:
    """Finds all job card elements using a configurable selector."""

    def __init__(self, card_selector: str):
        self._selector = card_selector

    def extract(self, html: str) -> List[Tag]:
        return BeautifulSoup(html, "lxml").select(self._selector)
