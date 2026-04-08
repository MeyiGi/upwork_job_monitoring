from loguru import logger

from src.domain.entities.job import Job
from src.domain.ports.llm_port import LLMPort
from src.domain.ports.notifier_port import NotifierPort
from src.domain.ports.repository_port import RepositoryPort


class JobProcessor:
    """Enriches and dispatches a single job. Knows nothing about scraping or loops."""

    def __init__(self, llm: LLMPort, notifier: NotifierPort, repo: RepositoryPort):
        self._llm = llm
        self._notifier = notifier
        self._repo = repo

    def process(self, job: Job) -> bool:
        if self._repo.exists(job.link):
            return False

        job.ai_summary = self._llm.summarize(job)
        self._notifier.send(job)
        self._repo.add(job.link)

        logger.success(f"[{job.source}] {job.title}")
        return True
