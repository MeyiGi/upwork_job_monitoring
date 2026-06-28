import json
from pathlib import Path
from loguru import logger

_FILE = Path("data/filter_config.json")


class FilterConfig:
    def __init__(self):
        self._max_age_minutes: int = self._load()

    def _load(self) -> int:
        if _FILE.exists():
            try:
                return int(json.loads(_FILE.read_text()).get("max_age_minutes", 60))
            except Exception:
                pass
        return 60

    def _save(self) -> None:
        _FILE.parent.mkdir(parents=True, exist_ok=True)
        _FILE.write_text(json.dumps({"max_age_minutes": self._max_age_minutes}))

    @property
    def max_age_minutes(self) -> int:
        return self._max_age_minutes

    def set_max_age(self, minutes: int) -> None:
        self._max_age_minutes = minutes
        self._save()
        logger.info(f"Max job age set to {minutes}m")


filter_config = FilterConfig()
