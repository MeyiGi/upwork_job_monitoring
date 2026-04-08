from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.job import Job


class LLMPort(ABC):

    @abstractmethod
    def summarize(self, job: Job) -> Optional[str]: ...
