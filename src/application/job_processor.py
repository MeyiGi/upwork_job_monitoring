import threading
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from loguru import logger

from src.domain.entities.job import Job
from src.domain.ports.llm_port import LLMPort
from src.domain.ports.notifier_port import NotifierPort
from src.domain.ports.repository_port import RepositoryPort
from src.config.settings import settings
from src.application.stats import stats


class JobProcessor:
    """Sends notification immediately, enriches with AI in background."""

    def __init__(self, llm: LLMPort, notifier: NotifierPort, repo: RepositoryPort):
        self._llm = llm
        self._notifier = notifier
        self._repo = repo
        self._blacklist = self._load_blacklist()
        logger.info(f"Blacklist: {self._blacklist or '(empty)'}")

    def _load_blacklist(self) -> list[str]:
        path = Path(settings.blacklist_file)
        if not path.exists():
            return []
        return [line.strip().lower() for line in path.read_text().splitlines() if line.strip()]

    def _is_blacklisted(self, job: Job) -> tuple[bool, str]:
        text = job.title.lower() + " " + (job.description or "").lower()
        for word in self._blacklist:
            if word in text:
                return True, word
        return False, ""

    def _is_too_old(self, job: Job) -> bool:
        if not job.posted:
            return False
        try:
            _BISHKEK = timezone(timedelta(hours=6))
            dt = datetime.strptime(job.posted, "%H:%M %Y-%m-%d").replace(tzinfo=_BISHKEK)
            return (datetime.now(_BISHKEK) - dt).total_seconds() > 3600
        except ValueError:
            return False

    def _is_zero_spend(self, job: Job) -> bool:
        spend = (job.client_spend or "").strip()
        if not spend:
            return True
        return bool(re.match(r"^\$0(\.0+)?[KMB]?$", spend, re.IGNORECASE))

    def process(self, job: Job) -> bool:
        if self._repo.exists(job.link):
            stats.add_seen()
            return False
        logger.info(f"Processing not in queue: {job.title}")
        # if self._is_zero_spend(job):
            # stats.add_zero_spend()
            # logger.info(f"  ✗ zero spend  — {job.title!r}")
            # return False

        if self._is_too_old(job):
            self._repo.add(job.link)
            logger.info(f"  ✗ too old (>1h)  — {job.title!r}")
            return False

        blacklisted, word = self._is_blacklisted(job)
        if blacklisted:
            stats.add_blacklist()
            logger.info(f"  ✗ blacklist '{word}'  — {job.title!r}")
            return False

        msg_id = self._notifier.send(job)
        self._repo.add(job.link)
        stats.add_sent()
        logger.success(f"  ✓ SENT  — {job.title!r}  |  {job.client_spend}  |  {job.budget}")

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
        else:
            logger.warning(f"  AI returned nothing — {job.title!r}")
