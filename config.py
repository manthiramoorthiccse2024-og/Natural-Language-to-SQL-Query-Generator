import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    database_path: str = os.getenv("DATABASE_PATH", "data/sample.db")
    max_rows: int = int(os.getenv("MAX_ROWS", "500"))
    query_timeout_seconds: int = int(os.getenv("QUERY_TIMEOUT_SECONDS", "5"))

settings = Settings()
