from pathlib import Path
from typing import Optional
from groq import Groq
from loguru import logger

from src.domain.entities.job import Job
from src.domain.ports.llm_port import LLMPort
from src.config.loader import load_prompt
from src.config.settings import settings


class GroqProvider(LLMPort):

    def __init__(self):
        self._client = Groq(api_key=settings.groq_api_key)
        self._template = load_prompt(
            str(Path(settings.prompts_dir) / "job_summary.txt")
        )

    def summarize(self, job: Job) -> Optional[str]:
        prompt = self._template.format(
            title=job.title,
            budget=job.budget or "—",
            level=job.contractor_tier or "—",
            skills=", ".join(job.skills),
            description=job.description or "—",
        )
        try:
            response = self._client.chat.completions.create(
                model=settings.groq_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=settings.groq_max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq error: {e}")
            return None
