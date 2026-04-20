"""
Configuration management for the SEO Monitor.

Loads settings from environment variables and .env files using pydantic-settings.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AnyHttpUrl, Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Project settings and configuration.

    Attributes:
        target_site_url: Base URL of the site to monitor (required).
        sitemap_path: Path to the sitemap (default: /sitemap.xml).
        crawler_concurrency: Max concurrent requests (1-20, default: 5).
        crawler_timeout: Request timeout in seconds (1-60, default: 10).
        crawler_user_agent: Custom User-Agent string.
        database_path: Path to the SQLite database file.
        feishu_webhook_url: Optional Feishu webhook URL for alerts.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Target Site
    target_site_url: AnyHttpUrl = Field(..., description="Base URL of the site to monitor")
    sitemap_path: str = Field(default="/sitemap.xml", description="Path to the sitemap")

    # Crawler Settings
    crawler_concurrency: int = Field(default=5, ge=1, le=20)
    crawler_timeout: int = Field(default=10, ge=1, le=60)
    crawler_user_agent: str = Field(default="SEO-Monitor/0.1")

    # Storage
    database_path: Path = Field(default=Path("data/seo_monitor.db"))

    # Notifications
    feishu_webhook_url: SecretStr | None = Field(default=None)

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")

    @model_validator(mode="after")
    def ensure_database_dir(self) -> "Settings":
        """
        Create parent directory of database_path if it doesn't exist.

        This is the only place in the codebase where directory creation is performed
        automatically during initialization.
        """
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        return self

    @property
    def database_url(self) -> str:
        """
        Return the SQLAlchemy async connection string for SQLite.

        Example: sqlite+aiosqlite:///D:/path/to/data/seo_monitor.db
        """
        return f"sqlite+aiosqlite:///{self.database_path.absolute()}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the cached Settings singleton.

    Settings are instantiated on first call and cached for subsequent calls.
    This lazy initialization prevents import-time validation errors.

    Usage:
        - Production: Use get_settings() to obtain the singleton.
        - Testing: Instantiate Settings() directly for isolation.
    """
    return Settings()  # type: ignore[call-arg]
