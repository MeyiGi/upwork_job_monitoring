from pathlib import Path
from loguru import logger

from src.config.settings import settings


class BlacklistManager:
    def __init__(self):
        self._path = Path(settings.blacklist_file)
        self._words: list[str] = self._load()

    def _load(self) -> list[str]:
        if not self._path.exists():
            return []
        return [line.strip().lower() for line in self._path.read_text().splitlines() if line.strip()]

    @property
    def words(self) -> list[str]:
        return self._words

    def add(self, word: str) -> bool:
        word = word.strip().lower()
        if not word or word in self._words:
            return False
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a") as f:
            f.write(word + "\n")
        self._words.append(word)
        logger.info(f"Blacklist += {word!r}")
        return True

    def remove(self, word: str) -> bool:
        word = word.strip().lower()
        if not word or word not in self._words:
            return False
        self._words.remove(word)
        self._path.write_text("\n".join(self._words) + ("\n" if self._words else ""))
        logger.info(f"Blacklist -= {word!r}")
        return True


blacklist = BlacklistManager()
