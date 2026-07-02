from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql://stock:stock@localhost:5432/stock"

    gemini_api_key: str = ""
    ai_analysis_max_rows: int = 500
    ai_analysis_query_timeout_ms: int = 5000

    frontend_url: str = "http://localhost:5173"
    admin_email: Optional[str] = None


settings = Settings()
