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
            self._sleep()

    def _cycle(self) -> None:
        seen: set[str] = set()
        for source, url in settings.sources.items():
            new = 0
            for job in self._scraper.scrape(url, source):
                if job.link not in seen:
                    seen.add(job.link)
                    if self._processor.process(job):
                        new += 1
            if new:
                logger.info(f"[{source}] sent {new} new jobs")
            self._repo.flush()

    def _sleep(self) -> None:
        delay = random.uniform(*settings.check_interval)
        logger.info(f"Next check in {int(delay // 60)}m {int(delay % 60)}s")
        time.sleep(delay)
