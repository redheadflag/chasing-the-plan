from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://ctp:ctp@localhost:5432/chasing_the_plan"
    # Comma-separated list of allowed CORS origins (frontend dev servers).
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
    sql_echo: bool = False

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
