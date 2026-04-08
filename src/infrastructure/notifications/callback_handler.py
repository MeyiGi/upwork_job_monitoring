import threading
import httpx
from loguru import logger


class CallbackHandler:
    """Listens for inline button presses, replies with description."""

    def __init__(self, token: str, chat_id: str, formatter):
        self._base = f"https://api.telegram.org/bot{token}"
        self._chat_id = chat_id
        self._formatter = formatter
        self._store: dict[str, str] = {}

    def register(self, message_id: int, description: str) -> None:
        self._store[str(message_id)] = description

    def start(self) -> None:
        threading.Thread(target=self._poll, daemon=True).start()
        logger.info("Callback handler started")

    def _poll(self) -> None:
        offset = None
        while True:
            try:
                updates = self._get_updates(offset)
                for update in updates:
                    offset = update["update_id"] + 1
                    self._handle(update)
            except Exception as e:
                logger.error(f"Polling error: {e}")

    def _get_updates(self, offset: int | None) -> list:
        params = {"timeout": 25, "allowed_updates": ["callback_query"]}
        if offset:
            params["offset"] = offset
        r = httpx.get(f"{self._base}/getUpdates", params=params, timeout=35)
        return r.json().get("result", [])

    def _handle(self, update: dict) -> None:
        cb = update.get("callback_query")
        if not cb:
            return

        msg_id = str(cb["message"]["message_id"])
        description = self._store.get(msg_id)

        httpx.post(f"{self._base}/answerCallbackQuery",
                   json={"callback_query_id": cb["id"]})

        if not description:
            return

        httpx.post(f"{self._base}/sendMessage", json={
            "chat_id": self._chat_id,
            "text": self._formatter.description_message(description),
            "parse_mode": "HTML",
            "reply_to_message_id": int(msg_id),
        }, timeout=httpx.Timeout(20.0, connect=10.0))
        httpx.post(f"{self._base}/editMessageReplyMarkup", json={
            "chat_id": self._chat_id,
            "message_id": int(msg_id),
            "reply_markup": {"inline_keyboard": []},
        })
