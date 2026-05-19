from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/openfitnessagent.db"
    APP_NAME: str = "OpenFitnessAgent"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENV: str = "local"
    LOG_LEVEL: str = "INFO"
    LOCAL_FIRST_MODE: bool = True
    SQLITE_BUSY_TIMEOUT_MS: int = 5000
    SQLITE_JOURNAL_MODE: str = "WAL"
    SQLITE_SYNCHRONOUS: str = "NORMAL"
    RETRY_ATTEMPTS: int = 3
    RETRY_BACKOFF_SECONDS: float = 0.2
    SCHEDULER_DAILY_CHECK_HOURS: int = 24
    SCHEDULER_WEEKLY_SUMMARY_DAYS: int = 7
    SCHEDULER_INACTIVITY_CHECK_HOURS: int = 6
    DEFAULT_SPLIT: List[str] = ["Push", "Pull", "Legs", "Rest", "Push", "Pull", "Legs"]
    PLATEAU_THRESHOLD: int = 3
    DELOAD_THRESHOLD: int = 6
    PROGRESSION_INCREMENT_KG: float = 2.5
    CONSISTENCY_WINDOW_DAYS: int = 30
    RECOVERY_FATIGUE_DECAY: float = 0.85

    model_config = {"env_prefix": "OFA_", "env_file": ".env", "extra": "ignore"}


settings = Settings()
