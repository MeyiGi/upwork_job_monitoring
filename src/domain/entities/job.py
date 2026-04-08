from pydantic import BaseModel
from typing import List, Optional


class Job(BaseModel):
    title: str
    link: str
    source: str
    posted: Optional[str] = None
    contractor_tier: Optional[str] = None
    budget: Optional[str] = None
    description: Optional[str] = None
    skills: List[str] = []
    proposals: Optional[str] = None
    country: Optional[str] = None
    client_spend: Optional[str] = None
    ai_summary: Optional[str] = None
