from functools import lru_cache

from pydantic import EmailStr, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    smtp_host: str | None = None
    smtp_port: int = Field(default=587, ge=1, le=65535)
    smtp_username: str | None = None
    smtp_password: SecretStr | None = None
    smtp_from_email: EmailStr | None = None
    contact_owner_email: EmailStr | None = None
    smtp_use_tls: bool = True
    smtp_timeout: float = Field(default=10, gt=0)
    gigachat_credentials: SecretStr | None = None
    gigachat_model: str = "GigaChat-2"
    gigachat_verify_ssl_certs: bool = True
    rate_limit_max_requests: int = Field(default=5, gt=0)
    rate_limit_window_seconds: int = Field(default=60, gt=0)
    cors_origins: str = "http://localhost:3000,http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    return Settings()
