import time
import random
from loguru import logger

from src.domain.ports.scraper_port import ScraperPort
from src.domain.ports.repository_port import RepositoryPort
from src.application.job_processor import JobProcessor
from src.config.settings import settings


class JobMonitor:
    """Runs the main loop. Delegates everything else."""

    def __init__(
        self,
        scraper: ScraperPort,
        processor: JobProcessor,
        repo: RepositoryPort,
    ):
        self._scraper = scraper
        self._processor = processor
        self._repo = repo

    def run(self) -> None:
        self._scraper.setup()
        while True:
            self._cycle()
            self._repo.flush()
            self._sleep()

    def _cycle(self) -> None:
        all_jobs = [
            job
            for source, url in settings.sources.items()
            for job in self._scraper.scrape(url, source)
        ]
        unique = list({j.link: j for j in all_jobs}.values())

        for job in unique:
            self._processor.process(job)

    def _sleep(self) -> None:
        delay = random.uniform(*settings.check_interval)
        logger.info(f"Next check in {int(delay // 60)}m {int(delay % 60)}s")
        time.sleep(delay)
