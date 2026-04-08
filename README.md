# Upwork Job Monitor

Monitors Upwork for new jobs and sends notifications to Telegram with AI summaries.

## Setup

1. Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Add your Upwork `cookies.json` to the root directory.

4. Run:
```bash
python main.py
```

## Project Structure

```
src/
├── domain/         # Business logic — no external dependencies
│   ├── entities/   # Job model
│   └── ports/      # Abstract interfaces (ScraperPort, LLMPort, etc.)
├── application/    # Use cases — JobProcessor, JobMonitor
└── infrastructure/ # Concrete implementations
    ├── scraping/   # Browser, PageFetcher, CardExtractor, JobMapper
    ├── llm/        # GroqProvider
    ├── notifications/ # TelegramNotifier, Formatter, CallbackHandler
    └── persistence/   # JsonQueueRepository

data/
├── prompts/        # LLM prompt templates (.txt)
└── selectors/      # CSS selectors per site (.yaml)
```

## Extending

- **New scraper site**: add `data/selectors/newsite.yaml` + implement `ScraperPort`
- **New LLM**: implement `LLMPort`
- **New notifier**: implement `NotifierPort`
- **New prompt**: edit `data/prompts/job_summary.txt`
- **Selectors changed**: edit `data/selectors/upwork.yaml` — no code changes needed
