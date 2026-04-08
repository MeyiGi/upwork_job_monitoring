from typing import Optional, List
from bs4 import Tag
import dateparser
from src.domain.entities.job import Job


class JobMapper:
    """
    Maps a single card Tag -> Job.
    All selectors and keywords come from config — nothing hardcoded.
    """

    _DATE_SETTINGS = {
        "TIMEZONE": "UTC",
        "TO_TIMEZONE": "Asia/Bishkek",
        "RETURN_AS_TIMEZONE_AWARE": True,
    }

    def __init__(self, fields: dict, budget_keywords: dict):
        self._f = fields
        self._bk = budget_keywords

    def map(self, card: Tag, source: str) -> Optional[Job]:
        title_el = card.select_one(self._f["title"])
        if not title_el:
            return None

        href = title_el.get("href", "")

        return Job(
            title=title_el.get_text(strip=True),
            link=f"https://www.upwork.com{href.split('?')[0]}",
            source=source,
            posted=self._parse_date(self._text(card, self._f["posted"])),
            contractor_tier=self._text(card, self._f["contractor_tier"]),
            budget=self._parse_budget(card),
            description=self._text(card, self._f["description"]),
            skills=self._texts(card, self._f["skills"]),
            proposals=self._text(card, self._f["proposals"]),
            country=self._text(card, self._f["country"]),
            client_spend=self._text(card, self._f["client_spend"]),
        )

    def _text(self, card: Tag, selector: str) -> Optional[str]:
        el = card.select_one(selector)
        return el.get_text(strip=True) if el else None

    def _texts(self, card: Tag, selector: str) -> List[str]:
        return [el.get_text(strip=True) for el in card.select(selector)]

    def _parse_date(self, text: Optional[str]) -> Optional[str]:
        if not text:
            return None
        dt = dateparser.parse(text, settings=self._DATE_SETTINGS)
        return dt.strftime("%H:%M %Y-%m-%d") if dt else None

    def _parse_budget(self, card: Tag) -> Optional[str]:
        job_type = self._text(card, self._f["job_type"]) or ""

        if self._bk["hourly"] in job_type:
            sep = self._bk["hourly_sep"]
            if sep in job_type:
                return f"{job_type.split(sep)[1].strip()}/hr"

        if self._bk["fixed"] in job_type:
            amount = self._text(card, self._f["budget"])
            return f"fixed {amount}" if amount else "fixed"

        return None
