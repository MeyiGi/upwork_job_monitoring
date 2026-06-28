import threading
import httpx
import time
from datetime import datetime
from loguru import logger
from src.application.stats import stats
from src.application.blacklist import blacklist
from src.application.filter_config import filter_config


class CallbackHandler:
    """Listens for inline button presses and /latest command."""

    def __init__(self, token: str, chat_id: str, formatter):
        self._base = f"https://api.telegram.org/bot{token}"
        self._chat_id = chat_id
        self._formatter = formatter
        self._store: dict[str, str] = {}
        self._titles: dict[str, str] = {}
        self._last_job_text: str | None = None
        self._backoff: int = 5

    def set_last_job(self, text: str) -> None:
        self._last_job_text = text

    def register(self, message_id: int, description: str) -> None:
        self._store[str(message_id)] = description

    def register_title(self, message_id: int, title: str) -> None:
        self._titles[str(message_id)] = title

    def start(self) -> None:
        httpx.get(f"{self._base}/deleteWebhook", params={"drop_pending_updates": "true"})
        httpx.post(f"{self._base}/setMyCommands", json={"commands": [
            {"command": "latest",    "description": "Show the latest job"},
            {"command": "stats",     "description": "Show statistics"},
            {"command": "status",    "description": "Show current filter settings"},
            {"command": "exclude",   "description": "Add keyword to blacklist"},
            {"command": "remove",    "description": "Remove keyword from blacklist"},
            {"command": "blacklist", "description": "Show all blacklist words"},
            {"command": "maxage",    "description": "Set max job age in minutes (e.g. /maxage 20)"},
        ]})
        threading.Thread(target=self._poll, daemon=True).start()
        logger.info("Callback handler started")

    def _poll(self) -> None:
        offset = None
        while True:
            try:
                updates = self._get_updates(offset)
                for update in updates:
                    offset = update["update_id"] + 1
                    try:
                        self._handle(update)
                    except Exception as e:
                        logger.error(f"Handle error: {e}")
            except Exception as e:
                logger.error(f"Polling error: {e}")
                time.sleep(self._backoff)  # теперь поле существует

    def _get_updates(self, offset: int | None) -> list:
        params = {"timeout": 25, "allowed_updates": ["callback_query", "message"]}
        if offset:
            params["offset"] = offset
        r = httpx.get(f"{self._base}/getUpdates", params=params, timeout=35)
        return r.json().get("result", [])

    def _handle(self, update: dict) -> None:
        if msg := update.get("message"):
            text = msg.get("text", "")
            logger.info(f"Message received: {text!r}")
            if text.startswith("/latest"):
                self._send_latest()
            elif text.startswith("/stats"):
                self._send_stats()
            elif text.startswith("/exclude"):
                self._add_exclude(text[len("/exclude"):].strip())
            elif text.startswith("/remove"):
                self._remove_exclude(text[len("/remove"):].strip())
            elif text.startswith("/blacklist"):
                self._send_blacklist()
            elif text.startswith("/maxage"):
                self._set_maxage(text[len("/maxage"):].strip())
            elif text.startswith("/status"):
                self._send_status()
            return

        cb = update.get("callback_query")
        if not cb:
            return

        msg_id = str(cb["message"]["message_id"])
        cb_data = cb.get("data", "")

        httpx.post(f"{self._base}/answerCallbackQuery",
                   json={"callback_query_id": cb["id"]})

        if cb_data == "title":
            title = self._titles.get(msg_id)
            if title:
                httpx.post(f"{self._base}/sendMessage", json={
                    "chat_id": self._chat_id,
                    "text": f"<code>{title}</code>",
                    "parse_mode": "HTML",
                    "reply_to_message_id": int(msg_id),
                }, timeout=httpx.Timeout(20.0, connect=10.0))
            return

        if cb_data == "desc":
            description = self._store.get(msg_id)
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

    def _send_status(self) -> None:
        uptime = datetime.now() - stats.started_at
        h, rem = divmod(int(uptime.total_seconds()), 3600)
        m = rem // 60
        words = blacklist.words
        text = (
            f"<b>Status</b>\n"
            f"<code>─────────────────────</code>\n"
            f"⏱  Max job age: <b>{filter_config.max_age_minutes} min</b>\n"
            f"🚫  Blacklist: <b>{len(words)} word{'s' if len(words) != 1 else ''}</b>\n"
            f"🟢  Running: <b>{h}h {m}m</b>"
        )
        httpx.post(f"{self._base}/sendMessage", json={
            "chat_id": self._chat_id,
            "text": text,
            "parse_mode": "HTML",
        }, timeout=httpx.Timeout(20.0, connect=10.0))

    def _send_blacklist(self) -> None:
        words = blacklist.words
        if not words:
            text = "Blacklist is empty."
        else:
            listed = "\n".join(f"  • <code>{w}</code>" for w in words)
            text = f"<b>Blacklist</b> ({len(words)} words)\n{listed}"
        httpx.post(f"{self._base}/sendMessage", json={
            "chat_id": self._chat_id,
            "text": text,
            "parse_mode": "HTML",
        }, timeout=httpx.Timeout(20.0, connect=10.0))

    def _remove_exclude(self, word: str) -> None:
        word = word.lower()
        if not word:
            text = "Usage: /remove &lt;keyword&gt;"
        elif blacklist.remove(word):
            text = f"✅ Removed from blacklist: <code>{word}</code>"
        else:
            text = f"⚠️ Not in blacklist: <code>{word}</code>"
        httpx.post(f"{self._base}/sendMessage", json={
            "chat_id": self._chat_id,
            "text": text,
            "parse_mode": "HTML",
        }, timeout=httpx.Timeout(20.0, connect=10.0))

    def _set_maxage(self, arg: str) -> None:
        try:
            minutes = int(arg)
            if minutes < 1:
                raise ValueError
            filter_config.set_max_age(minutes)
            text = f"✅ Max job age set to <b>{minutes} min</b>"
        except ValueError:
            text = f"Usage: /maxage &lt;minutes&gt;\nCurrent: <b>{filter_config.max_age_minutes} min</b>"
        httpx.post(f"{self._base}/sendMessage", json={
            "chat_id": self._chat_id,
            "text": text,
            "parse_mode": "HTML",
        }, timeout=httpx.Timeout(20.0, connect=10.0))

    def _add_exclude(self, word: str) -> None:
        word = word.lower()
        if not word:
            text = "Usage: /exclude &lt;keyword&gt;"
        elif blacklist.add(word):
            text = f"✅ Added to blacklist: <code>{word}</code>"
        else:
            text = f"⚠️ Already in blacklist: <code>{word}</code>"
        httpx.post(f"{self._base}/sendMessage", json={
            "chat_id": self._chat_id,
            "text": text,
            "parse_mode": "HTML",
        }, timeout=httpx.Timeout(20.0, connect=10.0))

    def _send_stats(self) -> None:
        httpx.post(f"{self._base}/sendMessage", json={
            "chat_id": self._chat_id,
            "text": stats.summary(),
            "parse_mode": "HTML",
        }, timeout=httpx.Timeout(20.0, connect=10.0))

    def _send_latest(self) -> None:
        if not self._last_job_text:
            httpx.post(f"{self._base}/sendMessage", json={
                "chat_id": self._chat_id,
                "text": "No jobs yet.",
            }, timeout=httpx.Timeout(20.0, connect=10.0))
            return
        httpx.post(f"{self._base}/sendMessage", json={
            "chat_id": self._chat_id,
            "text": self._last_job_text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }, timeout=httpx.Timeout(20.0, connect=10.0))