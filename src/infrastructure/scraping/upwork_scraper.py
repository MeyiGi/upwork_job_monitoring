from pathlib import Path
from typing import List
from loguru import logger

from src.domain.entities.job import Job
from src.domain.ports.scraper_port import ScraperPort
from src.infrastructure.scraping.browser import Browser
from src.infrastructure.scraping.page_fetcher import PageFetcher
from src.infrastructure.scraping.card_extractor import CardExtractor
from src.infrastructure.scraping.job_mapper import JobMapper
from src.config.loader import load_yaml
from src.config.settings import settings


class UpworkScraper(ScraperPort):

    def __init__(self):
        cfg = load_yaml(str(Path(settings.selectors_dir) / "upwork.yaml"))
        self._browser   = Browser(settings.cookies_file)
        self._fetcher   = PageFetcher(self._browser, settings.page_wait)
        self._extractor = CardExtractor(cfg["card"])
        self._mapper    = JobMapper(cfg["fields"], cfg["budget_keywords"])

    def setup(self) -> None:
        self._browser.apply_cookies()

    def scrape(self, url: str, source: str) -> List[Job]:
        html   = self._fetcher.fetch(url)
        cards  = self._extractor.extract(html)
        len(cards)
        jobs   = [self._mapper.map(c, source) for c in cards]
        result = [j for j in jobs if j]
        logger.info(f"[{source}] scraped {len(result)} jobs")
        return result
