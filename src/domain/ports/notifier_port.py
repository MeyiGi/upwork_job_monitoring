from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.job import Job


class NotifierPort(ABC):

    @abstractmethod
    def send(self, job: Job) -> Optional[int]: ...

    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def edit_summary(self, msg_id: int, job: Job) -> None: ...