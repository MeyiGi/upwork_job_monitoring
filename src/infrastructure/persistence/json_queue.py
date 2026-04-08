import json
from pathlib import Path
from collections import deque

from src.domain.ports.repository_port import RepositoryPort
from src.config.settings import settings


class JsonQueueRepository(RepositoryPort):

    def __init__(self):
        self._path = Path(settings.queue_file)
        self._queue: deque[str] = deque(
            self._load(), maxlen=settings.queue_size
        )

    def _load(self) -> list:
        if self._path.exists():
            return json.loads(self._path.read_text(encoding="utf-8"))
        return []

    def exists(self, job_id: str) -> bool:
        return job_id in self._queue

    def add(self, job_id: str) -> None:
        self._queue.append(job_id)

    def flush(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(list(self._queue), ensure_ascii=False),
            encoding="utf-8",
        )
