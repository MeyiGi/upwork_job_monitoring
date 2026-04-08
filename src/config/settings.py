from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Dict, Tuple


class Settings(BaseSettings):
    # Telegram
    telegram_token: str
    telegram_chat_id: str

    # Groq
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    groq_max_tokens: int = 300

    # Scraper
    sources: Dict[str, str] = Field(default_factory=dict)
    page_wait_min: int = 4
    page_wait_max: int = 8
    check_interval_min: int = 240
    check_interval_max: int = 600
    cookies_file: str = "cookies.json"

    # Storage
    queue_file: str = "data/queue.json"
    queue_size: int = 25

    # Paths
    prompts_dir: str = "data/prompts"
    selectors_dir: str = "data/selectors"

    @property
    def page_wait(self) -> Tuple[int, int]:
        return (self.page_wait_min, self.page_wait_max)

    @property
    def check_interval(self) -> Tuple[int, int]:
        return (self.check_interval_min, self.check_interval_max)

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"


settings = Settings()
