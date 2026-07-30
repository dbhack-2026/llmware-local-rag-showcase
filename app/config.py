from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LLMWARE_DEMO_", extra="ignore")

    model_name: str = "bling-answer-tool"
    knowledge_dir: Path = Path("knowledge")
    max_context_chars: int = 12000
    top_k: int = 4


settings = Settings()
