from abc import ABC, abstractmethod
from src.domain.entities.job import Job


class NotifierPort(ABC):

    @abstractmethod
    def send(self, job: Job) -> None: ...

    @abstractmethod
    def start(self) -> None: ...
