from pathlib import Path
from functools import lru_cache
import yaml


@lru_cache
def load_yaml(path: str) -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


@lru_cache
def load_prompt(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")
