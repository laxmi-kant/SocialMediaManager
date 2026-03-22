"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- Database ---
    database_url: str = "postgresql+asyncpg://smm:smmpass@localhost:5432/smm"
    database_url_sync: str = "postgresql://smm:smmpass@localhost:5432/smm"

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- Security ---
    secret_key: str = "change-me-to-a-random-256-bit-key"
    encryption_key: str = "change-me-to-a-fernet-key"

    # --- JWT ---
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # --- Claude AI ---
    anthropic_api_key: str = ""
    default_ai_model: str = "claude-haiku-4-5-20251001"

    # --- Twitter/X OAuth 2.0 ---
    twitter_client_id: str = ""
    twitter_client_secret: str = ""
    twitter_callback_url: str = "http://localhost:8000/api/v1/platforms/twitter/callback"

    # --- LinkedIn OAuth 2.0 ---
    linkedin_client_id: str = ""
    linkedin_client_secret: str = ""
    linkedin_callback_url: str = "http://localhost:8000/api/v1/platforms/linkedin/callback"

    # --- Reddit OAuth ---
    reddit_client_id: str = ""
    reddit_client_secret: str = ""

    # --- Dev.to ---
    devto_api_key: str = ""

    # --- Application ---
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"
    cors_origins: str = "http://localhost:3000"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
