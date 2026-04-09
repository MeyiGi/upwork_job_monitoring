import httpx
from loguru import logger

from src.domain.entities.job import Job
from src.domain.ports.notifier_port import NotifierPort
from src.infrastructure.notifications.formatter import TelegramFormatter
from src.infrastructure.notifications.callback_handler import CallbackHandler
from src.config.settings import settings


class TelegramNotifier(NotifierPort):

    def __init__(self):
        self._base = f"https://api.telegram.org/bot{settings.telegram_token}"
        self._chat_id = settings.telegram_chat_id
        self._formatter = TelegramFormatter()
        self._callbacks = CallbackHandler(
            token=settings.telegram_token,
            chat_id=settings.telegram_chat_id,
            formatter=self._formatter,
        )

    def start(self) -> None:
        self._callbacks.start()

    def send(self, job: Job) -> int | None:
        text = self._formatter.job_message(job)
        self._callbacks.set_last_job(text)
        response = httpx.post(f"{self._base}/sendMessage", json={
            "chat_id": self._chat_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
            "reply_markup": {
                "inline_keyboard": [[
                    {"text": "📋 Title", "callback_data": "title"},
                    {"text": "📝 Description", "callback_data": "desc"},
                ]]
            },
        }).json()

        if not response.get("ok"):
            logger.error(f"Telegram error: {response.get('description')}")
            return None

        msg_id = response["result"]["message_id"]
        self._callbacks.register_title(msg_id, job.title)
        if job.description:
            self._callbacks.register(msg_id, job.description)
        return msg_id

    def edit_summary(self, msg_id: int, job: Job) -> None:
        text = self._formatter.job_message(job)
        self._callbacks.set_last_job(text)
        httpx.post(f"{self._base}/editMessageText", json={
            "chat_id": self._chat_id,
            "message_id": msg_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
            "reply_markup": {
                "inline_keyboard": [[
                    {"text": "📝 Show description", "callback_data": "desc"}
                ]]
            },
        }, timeout=httpx.Timeout(20.0, connect=10.0))