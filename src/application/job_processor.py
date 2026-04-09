import threading
from pathlib import Path
from loguru import logger

from src.domain.entities.job import Job
from src.domain.ports.llm_port import LLMPort
from src.domain.ports.notifier_port import NotifierPort
from src.domain.ports.repository_port import RepositoryPort
from src.config.settings import settings


class JobProcessor:
    """Sends notification immediately, enriches with AI in background."""

    def __init__(self, llm: LLMPort, notifier: NotifierPort, repo: RepositoryPort):
        self._llm = llm
        self._notifier = notifier
        self._repo = repo
        self._blacklist = self._load_blacklist()

    def _load_blacklist(self) -> list[str]:
        path = Path(settings.blacklist_file)
        if not path.exists():
            return []
        return [line.strip().lower() for line in path.read_text().splitlines() if line.strip()]

    def _is_blacklisted(self, job: Job) -> bool:
        text = job.title.lower()
        return any(word in text for word in self._blacklist)

    def _is_zero_spend(self, job: Job) -> bool:
        spend = (job.client_spend or "").strip()
        if not spend:
            return True
        import re
        return bool(re.match(r"^\$0(\.0+)?[KMB]?$", spend, re.IGNORECASE))

    def process(self, job: Job) -> bool:
        if self._repo.exists(job.link):
            return False
        if self._is_zero_spend(job):
            logger.debug(f"[{job.source}] skipped (zero spend): {job.title}")
            return False
        if self._is_blacklisted(job):
            logger.debug(f"[{job.source}] skipped (blacklist): {job.title}")
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
