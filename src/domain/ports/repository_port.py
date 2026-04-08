from abc import ABC, abstractmethod


class RepositoryPort(ABC):

    @abstractmethod
    def exists(self, job_id: str) -> bool: ...

    @abstractmethod
    def add(self, job_id: str) -> None: ...

    @abstractmethod
    def flush(self) -> None: ...
