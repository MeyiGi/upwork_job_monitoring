from src.domain.entities.job import Job

SOURCE_LABELS = {
    "most-recent": "🕐 Most Recent",
    "best-matches": "⭐ Best Matches",
    # "my-feed":      "📰 My Feed",
}

TIER_ICONS = {
    "Entry level":  "🟢",
    "Intermediate": "🟡",
    "Expert":       "🔴",
}


class TelegramFormatter:

    def job_message(self, job: Job) -> str:
        return (
            f"🏷 <b>{SOURCE_LABELS.get(job.source, job.source)}</b>\n"
            f"🆕 <b>{self._e(job.title)}</b>\n\n"
            f"{self._budget_icon(job.budget)} <code>{self._e(job.budget)}</code>  "
            f"{TIER_ICONS.get(job.contractor_tier or '', '⚪')} "
            f"<code>{self._e(job.contractor_tier)}</code>\n"
            f"🕐 {self._e(job.posted)}  |  "
            f"📊 {self._e(job.proposals)}  |  "
            f"🌍 {self._e(job.country)}\n"
            f"💼 Client spent: {self._e(job.client_spend)}\n\n"
            f"🛠 {self._e(' • '.join(job.skills) if job.skills else '—')}\n"
            f"{self._summary_block(job)}"
            f"🔗 <a href='{job.link}'>Open job</a>"
        )

    def description_message(self, description: str) -> str:
        return f"📝 <b>Description:</b>\n\n{self._e(description)}"

    def _e(self, text: str | None) -> str:
        if not text:
            return "—"
        return (
            text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
        )

    def _budget_icon(self, budget: str | None) -> str:
        if not budget:
            return "💸"
        if "fixed" in budget:
            return "💰"
        if "/hr" in budget:
            return "⏱"
        return "💸"

    def _summary_block(self, job: Job) -> str:
        if not job.ai_summary:
            return ""
        return f"\n🤖 <b>AI:</b> {self._e(job.ai_summary)}\n\n"