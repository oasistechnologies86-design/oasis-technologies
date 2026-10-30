from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


PRODUCTION_FRONTEND_ORIGIN = "https://oasis-technologies-pearl.vercel.app"


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./oasis_dev.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    admin_email: str = ""
    admin_password_hash: str = ""
    jwt_secret: str = ""
    jwt_access_token_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def allowed_origins(self):
        # Keep environment-configured origins, and always allow the live frontend.
        # This avoids a production CORS outage if CORS_ORIGINS is missing or blank.
        origins = [
            origin.strip().rstrip("/")
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]
        if PRODUCTION_FRONTEND_ORIGIN not in origins:
            origins.append(PRODUCTION_FRONTEND_ORIGIN)
        return origins


@lru_cache
def get_settings():
    return Settings()
