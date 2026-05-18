from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/openfitnessagent.db"
    APP_NAME: str = "OpenFitnessAgent"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    DEFAULT_SPLIT: List[str] = ["Push", "Pull", "Legs", "Rest", "Push", "Pull", "Legs"]
    PLATEAU_THRESHOLD: int = 3
    DELOAD_THRESHOLD: int = 6
    PROGRESSION_INCREMENT_KG: float = 2.5
    CONSISTENCY_WINDOW_DAYS: int = 30
    RECOVERY_FATIGUE_DECAY: float = 0.85

    model_config = {"env_prefix": "OFA_", "env_file": ".env", "extra": "ignore"}


settings = Settings()
