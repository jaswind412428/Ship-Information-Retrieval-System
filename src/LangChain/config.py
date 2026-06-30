"""集中管理 LangChain 與模型設定。"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """從環境變數或專案根目錄的 .env 載入設定。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_provider: Literal["ollama", "openai"] = "ollama"

    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_chat_model: str = "qwen2.5:7b"

    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"
    openai_temperature: float = Field(default=0, ge=0, le=2)
    openai_timeout_seconds: float = Field(default=60, gt=0)
    openai_max_retries: int = Field(default=2, ge=0)


@lru_cache
def get_settings() -> Settings:
    """回傳單例設定，避免每次請求都重新讀取環境變數。"""

    return Settings()  # type: ignore[call-arg]
