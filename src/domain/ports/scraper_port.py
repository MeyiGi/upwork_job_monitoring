from abc import ABC, abstractmethod
from typing import List
from src.domain.entities.job import Job


class ScraperPort(ABC):

    @abstractmethod
    def scrape(self, url: str, source: str) -> List[Job]: ...

    @abstractmethod
    def setup(self) -> None: ...
