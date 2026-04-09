import threading
from loguru import logger

from src.domain.entities.job import Job
from src.domain.ports.llm_port import LLMPort
from src.domain.ports.notifier_port import NotifierPort
from src.domain.ports.repository_port import RepositoryPort


class JobProcessor:
    """Sends notification immediately, enriches with AI in background."""

    def __init__(self, llm: LLMPort, notifier: NotifierPort, repo: RepositoryPort):
        self._llm = llm
        self._notifier = notifier
        self._repo = repo

    def process(self, job: Job) -> bool:
        if self._repo.exists(job.link):
            return False

        msg_id = self._notifier.send(job)
        self._repo.add(job.link)
        logger.success(f"[{job.source}] {job.title}")

        if msg_id:
            threading.Thread(
                target=self._enrich, args=(job, msg_id), daemon=True
            ).start()
        return True

    def _enrich(self, job: Job, msg_id: int) -> None:
        summary = self._llm.summarize(job)
        if summary:
            job.ai_summary = summary
            self._notifier.edit_summary(msg_id, job)
