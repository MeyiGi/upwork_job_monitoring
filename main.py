from loguru import logger

from src.infrastructure.scraping.upwork_scraper import UpworkScraper
from src.infrastructure.llm.groq_provider import GroqProvider
from src.infrastructure.notifications.telegram_notifier import TelegramNotifier
from src.infrastructure.persistence.json_queue import JsonQueueRepository
from src.application.job_processor import JobProcessor
from src.application.monitor import JobMonitor


def main() -> None:
    logger.add("logs/monitor.log", rotation="1 day", retention="7 days")

    scraper   = UpworkScraper()
    llm       = GroqProvider()
    notifier  = TelegramNotifier()
    repo      = JsonQueueRepository()

    notifier.start()

    processor = JobProcessor(llm=llm, notifier=notifier, repo=repo)
    monitor   = JobMonitor(scraper=scraper, processor=processor, repo=repo)

    monitor.run()


if __name__ == "__main__":
    main()
