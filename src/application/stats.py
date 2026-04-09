import json
from datetime import datetime, date
from pathlib import Path

_FILE = Path("data/stats.json")


class Stats:
    def __init__(self):
        self.started_at = datetime.now()
        # session (resets on restart)
        self.session_sent = 0
        self.session_zero_spend = 0
        self.session_blacklist = 0
        self.skipped_seen = 0
        # daily (persisted, resets at midnight)
        self._load()

    def _load(self):
        today = str(date.today())
        if _FILE.exists():
            data = json.loads(_FILE.read_text())
            if data.get("date") == today:
                self.day_sent = data.get("sent", 0)
                self.day_zero_spend = data.get("zero_spend", 0)
                self.day_blacklist = data.get("blacklist", 0)
                return
        self.day_sent = 0
        self.day_zero_spend = 0
        self.day_blacklist = 0

    def _save(self):
        _FILE.parent.mkdir(parents=True, exist_ok=True)
        _FILE.write_text(json.dumps({
            "date": str(date.today()),
            "sent": self.day_sent,
            "zero_spend": self.day_zero_spend,
            "blacklist": self.day_blacklist,
        }))

    def add_sent(self):
        self.session_sent += 1
        self.day_sent += 1
        self._save()

    def add_zero_spend(self):
        self.session_zero_spend += 1
        self.day_zero_spend += 1
        self._save()

    def add_blacklist(self):
        self.session_blacklist += 1
        self.day_blacklist += 1
        self._save()

    def add_seen(self):
        self.skipped_seen += 1

    def summary(self) -> str:
        uptime = datetime.now() - self.started_at
        h, rem = divmod(int(uptime.total_seconds()), 3600)
        m = rem // 60
        today = datetime.now().strftime("%d %b")

        def row(label: str, val: int) -> str:
            return f"<code>{label:<14}</code>  <b>{val}</b>"

        return (
            f"<b>Stats</b>\n"
            f"<code>─────────────────────</code>\n"
            f"📅  <b>Today</b> ({today})\n"
            f"{row('  sent', self.day_sent)}\n"
            f"{row('  zero spend', self.day_zero_spend)}\n"
            f"{row('  blacklisted', self.day_blacklist)}\n"
            f"<code>─────────────────────</code>\n"
            f"🔄  <b>This session</b>\n"
            f"{row('  sent', self.session_sent)}\n"
            f"{row('  zero spend', self.session_zero_spend)}\n"
            f"{row('  blacklisted', self.session_blacklist)}\n"
            f"{row('  already seen', self.skipped_seen)}\n"
            f"<code>─────────────────────</code>\n"
            f"⏱  uptime  <b>{h}h {m}m</b>"
        )


stats = Stats()
