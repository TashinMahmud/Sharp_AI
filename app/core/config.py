
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    debug: bool = False
    memory_max_turns: int = 20
    memory_keep_last: int = 10


@lru_cache
def get_settings() -> Settings:
    return Settings()
